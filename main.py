from tools.pdf_tool import PDFSummaryTool
from tools.slack_tool import SlackNotifierTool

def run_agent(prompt: str):
    summary = PDFSummaryTool.run(prompt)
    print("\nSummary:\n", summary)
    SlackNotifierTool.run(summary)

#Pass in a prompt for PDF summarization
if __name__ == "__main__":
    test_prompt = "Summarize the PDF from here https://static.googleusercontent.com/media/research.google.com/en//archive/mapreduce-osdi04.pdf for me"
    run_agent(test_prompt)
