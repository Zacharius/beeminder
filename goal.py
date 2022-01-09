import datetime
import json
import requests

from vars import BEEMINDER_TOKEN, USERNAME

URL = "https://www.beeminder.com/api/v1/"


class Goal:

    def __init__(self, goal_dict=None, notion_db=None):
        self.goal_type = None
        self.__dict__ = goal_dict
        if not hasattr(self, "datapoints"):
            self.__dict__.update(self.__load_data_from_api())

        self.datapoints = self.datapoints[::-1]

        if notion_db:
            self.__get_params_from_notion()

        if not hasattr(self, "buffer_threshold"):
            self.buffer_threshold = 3
        if not hasattr(self, "goal_rate"):
            self.goal_rate = None
        if not hasattr(self, "step_rate"):
            self.step_rate = None


    @staticmethod
    def get_user_goals_names():
        goal_list = beeminder_api_call("/goals.json?auth_token=" + BEEMINDER_TOKEN)
        return goal_list

    def __load_data_from_api(self):
        data = beeminder_api_call("/goals/" + self.slug + ".json?auth_token=" + BEEMINDER_TOKEN + "&datapoints=true")
        return data

    def __get_params_from_notion(self):
        self.step_rate = self.notion_row.step_rate
        self.goal_rate = self.notion_row.goal_rate
        self.buffer_threshold = self.notion_row.buffer_threshold


    def cur_rate(self):

        if self.goal_type in ["hustler", "drinker"]:

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

            for point in self.datapoints:
                timestamp = int(point["daystamp"])
                if timestamp < cutoff:
                    return sum
                sum += point['value']
            return sum
        else:
            return 0

    # Decides whether goal can increment based on actual rate vs rate limit
    # returns boolean
    def can_increment(self):
        if not self.goal_rate:
            return False

        if self.goal_type == 'hustler':
            return self.rate < self.goal_rate
        elif self.goal_type == 'drinker':
            return self.rate > self.goal_rate

    # decides whether buffer is in a safe state
    # returns boolean
    def safe_buffer(self):
        if not self.buffer_threshold:
            return False

        return self.buffer_threshold <= self.safebuf

    # decides whether rate over last period is greater than set rate
    def safe_rate(self):
        if not self.goal_type in ["hustler", "drinker"]:
           return True

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
        if (self.goal_type == "hustler" and new_rate > self.goal_rate) or (self.goal_type == "drinker" and new_rate < self.goal_rate):
            new_rate = self.rate_limi


        if not dry_run:
            old_rate_end_date = (datetime.datetime.today() + datetime.timedelta(days=6)).strftime("%Y-%m-%d")
            new_rate_end_date = (datetime.datetime.today() + datetime.timedelta(days=3650)).strftime("%Y-%m-%d")
            self.roadall[-1][0] = old_rate_end_date
            self.roadall.append([new_rate_end_date, None, new_rate])
            payload = {
                "auth_token": BEEMINDER_TOKEN,
                "roadall": json.dumps(self.roadall)
            }
            beeminder_api_call("/goals/" + self.slug + ".json", payload=payload)

        return new_rate

    def entered_data_today(self):
        last_daystamp = self.datapoints[0]["daystamp"]
        todaystamp = datetime.date.today().strftime("%Y%m%d")
        return todaystamp == last_daystamp

    def sync_notion_to_beeminder(self):
        safe = (self.safe_buffer() or self.entered_data_today()) and bool(self.safebuf)
        self.notion_row.safe = safe
        self.notion_row.buffer_days = self.safebuf
        self.notion_row.frequency = str(round(self.cur_rate(), 1)) + "/" + str(self.runits)
        self.notion_row.rate = str(self.rate) + "/" + str(self.runits)


def beeminder_api_call(call_str, payload=None):
    request_stub = URL + "/users/" + USERNAME
    url = request_stub + call_str
    if payload:
        resp = requests.put(url, data=payload)
    else:
        resp = requests.get(url)

    if resp.status_code != 200:
        print("Error Code: %s" % resp.status_code)
        print("Error Text: %s" % resp.text)
        print("Request : %s" % url)

    return resp.json()


def get_all_goals():

    goals = beeminder_api_call("/goals.json?auth_token=" + BEEMINDER_TOKEN + "&datapoints=true")
    return [Goal(goal_dict=goal) for goal in goals]


if __name__ == '__main__':
    goals = get_all_goals()
    for goal in goals:
        goal.sync_notion_to_beeminder()