import json

from notion_client import Client

from vars import NOTION_TOKEN, HABIT_TABLE_ID
from goal import get_all_goals

notion = Client(auth=NOTION_TOKEN)


def sync_habit_table():
    # bee_2_notion_props ={
    #     "runits": "period",
    #     "rate": "set_rate",
    #     "name": "slug",
    #     "buffer_days": "safebuf",
    #     "goal_type": "goal_type"
    # }

    def insert_select(val):
        return {
            "select": {
                "name": val
            }
        }

    def insert_text(val):
        return {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": val
                    }
                }
            ]
        }

    def insert_num(val):
        return {
            "number": val
        }

    def insert_checkbox(val):
        return {
            "checkbox": val
        }

    # collection = client.get_collection_view(NOTION_CV_URL).collection
    goals = get_all_goals()
    for goal in goals:
        filter = {
            "property": "Name",
            "text": {"equals": goal.slug}
        }

        # notion_row = get_or_create_row(collection, goal.slug)

        res = notion.databases.query(database_id=HABIT_TABLE_ID, filter=filter)
        if len(res["results"]) != 1:
            print(f"{goal.slug} Failed")
            continue

        page_id = res["results"][0]["id"]

        goal_rate = str(goal.rate) + "/" + str(goal.runits)
        actual_rate = str(round(goal.cur_rate(), 1)) + "/" + str(goal.runits)
        safe = (goal.safe_buffer() or goal.entered_data_today()) and bool(goal.safebuf)
        update_payload = {
            "period": insert_select(goal.runits),
            "actual_rate": insert_text(actual_rate),
            "safe": insert_checkbox(safe),
            "buffer_days": insert_num(goal.safebuf),
            "goal_rate": insert_text(goal_rate)

        }
        notion.pages.update(page_id=page_id, properties=update_payload)
        print(f"{goal.slug} Succeeded")


