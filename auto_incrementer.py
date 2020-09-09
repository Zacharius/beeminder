from goal import Goal
from vars import GOALS
from goal import get_all_goals


def auto_increment(dry_run=True):
    for goal in get_all_goals():
        if goal.safe_to_increment():
            print("incrementing goal %s from %s to %s a %s" % (goal.name, goal.rate, goal.rate+goal.step_rate, goal.runits))
            goal.increment_rate(dry_run=dry_run)
        else:
            print("goal %s not safe to increment" % goal.slug)


if __name__ == "__main__":
    auto_increment(False)

