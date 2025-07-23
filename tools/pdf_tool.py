import re
import requests
import fitz  #PyMuPDF
from langchain.tools import tool
import vertexai
from vertexai.generative_models import GenerativeModel

#Initialize Vertex AI for existing project
vertexai.init(project="add your project ID", location="us-central1")

@tool(description="Extracts a PDF link from the prompt, downloads and summarizes it using Gemini.")
def PDFSummaryTool(prompt: str) -> str:

    #Extract PDF URL from prompt
    url_match = re.search(r'(https?://\S+\.pdf)', prompt)
    if not url_match:
        return "No PDF link found in the prompt."

    pdf_url = url_match.group(1)

    #Download the PDF
    response = requests.get(pdf_url)
    if response.status_code != 200:
        return f"Failed to download PDF: {response.status_code}"

    with open("/tmp/temp.pdf", "wb") as f:
        f.write(response.content)

    #Extract text using PyMuPDF
    doc = fitz.open("/tmp/temp.pdf")
    text = "".join([page.get_text() for page in doc])
    doc.close()

    if not text.strip():
        return "Could not extract any text from the PDF."

    #Summarize using Gemini 
    model = GenerativeModel("gemini-2.0-flash")
    result = model.generate_content(
        f"Summarize this document:\n\n{text[:4000]}",
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 300,
        }
    )

    return result.text.strip()
