import requests
from langchain.tools import tool

#use webhook created from slack app
SLACK_WEBHOOK_URL = "Add your slack webhook URL here"

@tool(description="Send a message to a Slack webhook")
def SlackNotifierTool(message: str) -> str:

    #Posts a message to Slack using webhook URL
    res = requests.post(SLACK_WEBHOOK_URL, json={"text": message})
    return "Posted to Slack" if res.status_code == 200 else f"Slack error: {res.text}"
