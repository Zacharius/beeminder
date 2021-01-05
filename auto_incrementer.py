from goal import Goal, get_all_goals
from notion_integration import get_collection


def auto_increment(dry_run=True):
    collection = get_collection()
    for goal in get_all_goals(collection):
        if goal.safe_to_increment():
            print("incrementing goal %s from %s to %s a %s" % (goal.slug, goal.rate, goal.rate+goal.step_rate, goal.runits))
            goal.increment_rate(dry_run=dry_run)
        else:
            print("goal %s not safe to increment" % goal.slug)
            print(goal.safe_type())
            print(goal.can_increment())
            print(goal.safe_buffer())
            print(goal.safe_rate())


if __name__ == "__main__":
    auto_increment(True)

