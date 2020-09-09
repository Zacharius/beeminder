from goal import Goal
from vars import GOALS
from goal import get_all_goals


def auto_increment(dry_run=True):
    for goal in get_all_goals():
        if goal.safe_to_increment():
            print(f"incrementing goal {goal.name} from {goal.rate} to {goal.rate+goal.step_rate} a {goal.runits}")
            goal.increment_rate(dry_run=dry_run)
        else:
            print(f"goal {goal.slug} not safe to increment")


if __name__ == "__main__":
    auto_increment(False)

