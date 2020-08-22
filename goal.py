import datetime
import json
import requests

from vars import TOKEN, USERNAME

URL = "https://www.beeminder.com/api/v1/"



class Goal:

    def __init__(self, dict):
        self.__dict__ = dict
        self.__dict__.update(self.__load_data_from_api())


    @staticmethod
    def get_user_goals_names():
        request = URL + "/users/" + USERNAME + "/goals.json?auth_token=" + TOKEN
        resp = requests.get(request)
        goal_list = resp.json()
        return goal_list

    def __load_data_from_api(self):
        request = URL + "/users/" + USERNAME + "/goals/" + self.name + ".json?auth_token=" + TOKEN + "&datapoints=true"
        r = requests.get(request)
        data = r.json()
        return data

    def cur_rate(self):

        if self.runits == 'y':
            period = 365
        elif self.runits == 'm':
            period = 30
        elif self.runits == 'w':
            period = 7
        else:
            return None

        def get_past_timestamp(delta_days):
            now = datetime.datetime.utcnow()
            time = now - datetime.timedelta(days=delta_days)
            return int(time.strftime('%Y%m%d'))

        cutoff = get_past_timestamp(period)

        sum = 0

        for point in reversed(self.datapoints):
            timestamp = int(point['daystamp'])
            if timestamp < cutoff:
                return sum
            sum += point['value']
        return sum

    # Decides whether goal can increment based on actual rate vs rate limit
    # returns boolean
    def can_increment(self):
        if self.goal_type == 'hustler':
            return self.rate < self.rate_limit
        elif self.goal_type == 'drinker':
            return self.rate > self.rate_limit

    # decides whether buffer is in a safe state
    # returns boolean
    def safe_buffer(self):
        return self.buffer_threshold <= self.safebuf

    # decides whether rate over last period is greater than set rate
    def safe_rate(self):
        cur_rate = self.cur_rate()
        if self.goal_type == "hustler":
            return cur_rate >= self.rate
        elif self.goal_type == 'drinker':
            return cur_rate <= self.rate

    def safe_type(self):
        return self.goal_type in ["hustler", "drinker"]

    def safe_to_increment(self):
        return self.safe_type() and self.can_increment() and self.safe_buffer() and self.safe_rate()

    def increment_rate(self, dry_run=True):
        new_rate = self.rate + self.step_rate
        if (self.goal_type == "hustler" and new_rate > self.rate_limit) or (self.goal_type == "drinker" and new_rate < self.rate_limit):
            new_rate = self.rate_limi


        if not dry_run:
            old_rate_end_date = (datetime.datetime.today() + datetime.timedelta(days=6)).strftime("%Y-%m-%d")
            new_rate_end_date = (datetime.datetime.today() + datetime.timedelta(days=3650)).strftime("%Y-%m-%d")
            self.roadall[-1][0] = old_rate_end_date
            self.roadall.append([new_rate_end_date, None, new_rate])
            payload = {
                "auth_token": TOKEN,
                "roadall": json.dumps(self.roadall)
            }
            request_url = URL + "/users/" + USERNAME + "/goals/" + self.name + ".json"
            resp = requests.put(request_url, data=payload)
            if resp.status_code != 200:
                print(f"Error Incrementing Goal {self.name}")
                print(f"Error Code: {resp.status_code}")
                print(f"Error Text: {resp.text}")

        return new_rate