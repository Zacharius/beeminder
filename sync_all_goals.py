

from goal import get_all_goals
from notion_integration import get_collection

collection = get_collection()
goals = get_all_goals(collection)
for goal in goals:
    goal.sync_notion_to_beeminder()
