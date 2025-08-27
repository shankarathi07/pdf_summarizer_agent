"""
This script summarizes a PDF from a URL and sends the summary to Slack.

It takes a prompt containing a PDF URL as a command-line argument.
The script uses the pdf_summary_tool to generate the summary and the
slack_notifier_tool to send it to a Slack channel.

Usage:
    python main.py "Your prompt with a link to a PDF like http://example.com/file.pdf"
"""

import argparse
from dotenv import load_dotenv
from tools.pdf_tool import pdf_summary_tool
from tools.slack_tool import slack_notifier_tool

# Load environment variables from .env file
load_dotenv()

def run_agent(prompt: str):
    """
    Runs the PDF summarization and Slack notification agent.

    Args:
        prompt: The user prompt, which should contain a URL to a PDF.
    """
    print("Starting agent...")
    summary = pdf_summary_tool.run(prompt)
    print("\nSummary:\n", summary)

    if "error" not in summary.lower():
        print("Sending summary to Slack...")
        slack_result = slack_notifier_tool.run(summary)
        print(f"Slack notification result: {slack_result}")
    else:
        print("Skipping Slack notification due to summary error.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize a PDF and send the summary to Slack.")
    parser.add_argument("prompt", type=str, help="The prompt containing the PDF URL.")
    args = parser.parse_args()

    run_agent(args.prompt)
