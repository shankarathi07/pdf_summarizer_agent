"""
This module provides a tool to summarize a PDF from a URL.

It extracts a PDF link from a prompt, downloads the PDF, extracts the text,
and then uses the Gemini model to generate a summary.
"""

import os
import re
import requests
import fitz  # PyMuPDF
import tempfile
import vertexai
from langchain.tools import tool
from vertexai.generative_models import GenerativeModel

# --- CONFIGURATION ---
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
if not GCP_PROJECT_ID:
    raise ValueError("GCP_PROJECT_ID environment variable not set.")
vertexai.init(project=GCP_PROJECT_ID, location="us-central1")

# The maximum number of characters to send to the summarization model.
MAX_TEXT_LENGTH = 4000

# --- HELPER FUNCTIONS ---

def _extract_pdf_url(prompt: str) -> str | None:
    """Extracts the first PDF URL found in a prompt."""
    url_match = re.search(r'(https?://\S+\.pdf)', prompt)
    return url_match.group(1) if url_match else None

def _download_pdf(url: str, temp_path: str) -> None:
    """Downloads a PDF from a URL to a temporary path."""
    response = requests.get(url)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    with open(temp_path, "wb") as f:
        f.write(response.content)

def _extract_text_from_pdf(temp_path: str) -> str:
    """Extracts all text from a PDF file."""
    doc = fitz.open(temp_path)
    text = "".join([page.get_text() for page in doc])
    doc.close()
    return text

def _summarize_text_with_gemini(text: str) -> str:
    """Summarizes text using the Gemini model."""
    model = GenerativeModel("gemini-2.0-flash")
    result = model.generate_content(
        f"Summarize this document:\n\n{text[:MAX_TEXT_LENGTH]}",
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 300,
        }
    )
    return result.text.strip()

# --- MAIN TOOL ---

@tool(description="Extracts a PDF link from the prompt, downloads and summarizes it using Gemini.")
def pdf_summary_tool(prompt: str) -> str:
    """
    Summarizes a PDF from a URL found in the prompt.

    Args:
        prompt: The user prompt, which should contain a URL to a PDF.

    Returns:
        The summary of the PDF, or an error message.
    """
    # 1. Extract URL
    pdf_url = _extract_pdf_url(prompt)
    if not pdf_url:
        return "No PDF link found in the prompt."

    # Use a context manager for the temporary file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as temp_file:
        temp_pdf_path = temp_file.name

        try:
            # 2. Download PDF
            _download_pdf(pdf_url, temp_pdf_path)

            # 3. Extract text
            text = _extract_text_from_pdf(temp_pdf_path)
            if not text.strip():
                return "Could not extract any text from the PDF."

            # 4. Summarize text
            summary = _summarize_text_with_gemini(text)
            return summary

        except requests.HTTPError as e:
            return f"Failed to download PDF: {e}"
        except Exception as e:
            # Catch other potential errors during processing
            return f"An error occurred: {e}"
