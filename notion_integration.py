from notion.client import NotionClient

from vars import GOALS, NOTION_TOKEN, NOTION_CV_URL
#from goal import Goal, get_all_goals
#from auto_incrementer import intake_goals

class Goal_Table():

    def __init__(self):
        client = NotionClient(token_v2=NOTION_TOKEN)
        self.rows = client.get_collection_view(NOTION_CV_URL).collection.get_rows()

def get_collection():
    client = NotionClient(token_v2=NOTION_TOKEN)

    return client.get_collection_view(NOTION_CV_URL).collection

def sync_goal_table(goals, client=None):
    bee_2_notion_props ={
        "runits": "period",
        "rate": "set_rate",
        "name": "slug",
        "buffer_days": "safebuf",
        "goal_type": "goal_type"
    }

    if not client:
        client = NotionClient(token_v2=NOTION_TOKEN)

    collection = client.get_collection_view(NOTION_CV_URL).collection
    for goal in goals:
        notion_row = get_or_create_row(collection, goal.slug)

        #for props in bee_2_notion_props.keys():
        #    notion_row[bee_2_notion_props[]]
        if notion_row:
            safe = (goal.safe_buffer() or goal.entered_data_today()) and bool(goal.safebuf)
            notion_row.safe = safe
            notion_row.buffer_days = str(goal.safebuf)
            notion_row.frequency = str(round(goal.cur_rate(), 1)) + "/" + str(goal.runits)
            notion_row.rate = str(goal.rate) + "/" + str(goal.runits)


def get_or_create_row(collection, goal_title):
    for row in collection.get_rows():
        if row.title.lower() == goal_title:
            return row

    row = collection.add_row()
    row.name = goal_title


