import requests
from datetime import datetime, timedelta

from vars import USERNAME, TOKEN, GOALS


def rate(goal, num_days):
    url = "https://www.beeminder.com/api/v1/"
    request = url + "/users/" + USERNAME + "/goals/" + goal + "/datapoints.json?auth_token=" + TOKEN
    r = requests.get(request)
    data = r.json()

    def get_timestamp(delta_days):
        now = datetime.utcnow()
        time = now - timedelta(days=delta_days)
        return int(time.strftime('%Y%m%d'))

    w_time = get_timestamp(7)
    m_time = get_timestamp(30)
    q_time = get_timestamp(90)

    sum = 0
    w_avg = 0
    m_avg = 0
    q_avg = 0

    for point in data:
        timestamp = int(point['daystamp'])
        if timestamp < w_time and not w_avg:
            w_avg = sum/7 * num_days
        if timestamp < m_time and not m_avg:
            m_avg = sum/30 * num_days
        if timestamp < q_time:
            q_avg = sum/90 * num_days
            break

        sum += point['value']

    return w_avg, m_avg, q_avg


if __name__ == "__main__":
    for goal, dur in GOALS:
        num_days = 1
        if dur is 'w':
            num_days = '7'
        if dur is 'm':
            num_days = '30'

        w, m, q = rate(goal, int(num_days))
        print(f'{goal} | {w:.2f}/{dur} | {m:.2f}/{dur} | {q:.2f}/{dur} |')

    print("Done")
