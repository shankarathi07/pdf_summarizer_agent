"""
This module provides a tool to send a message to a Slack webhook.
"""

import os
import requests
from langchain.tools import tool

# --- CONFIGURATION ---
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
if not SLACK_WEBHOOK_URL:
    raise ValueError("SLACK_WEBHOOK_URL environment variable not set.")

# --- MAIN TOOL ---

@tool(description="Send a message to a Slack webhook")
def slack_notifier_tool(message: str) -> str:
    """
    Posts a message to a Slack channel using a webhook URL.

    Args:
        message: The message to post to Slack.

    Returns:
        A string indicating success or failure.
    """
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json={"text": message})
        response.raise_for_status()  # Raise an exception for bad status codes
        return "Posted to Slack"
    except requests.exceptions.RequestException as e:
        return f"Slack error: {e}"
