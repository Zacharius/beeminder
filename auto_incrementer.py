from goal import Goal
from vars import GOALS
from notion_integration import sync_goal_table

import sys

#return array of goal objects from locally stored array of goal dicts
def intake_goals():
    return [Goal(goal) for goal in GOALS]


def auto_incrementer(dry_run=True):
    for goal in intake_goals():
        if goal.safe_to_increment():
            print(f"incrementing goal {goal.name} from {goal.rate} to {goal.rate+goal.step_rate} a {goal.runits}")
            goal.increment_rate(dry_run=dry_run)
        else:
            print(f"goal {goal.name} not safe to increment")


if __name__ == "__main__":
    auto_incrementer()

