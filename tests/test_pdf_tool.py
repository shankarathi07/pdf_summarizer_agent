import pytest
from tools import pdf_tool
from unittest.mock import MagicMock, patch, mock_open

# --- Tests for Helper Functions ---

def test_extract_pdf_url():
    """Tests the _extract_pdf_url helper function."""
    prompt_with_url = "Here is a url http://example.com/file.pdf for you"
    prompt_without_url = "There is no url here"
    assert pdf_tool._extract_pdf_url(prompt_with_url) == "http://example.com/file.pdf"
    assert pdf_tool._extract_pdf_url(prompt_without_url) is None

@patch('requests.get')
def test_download_pdf_success(mock_get):
    """Tests the _download_pdf helper function for a successful download."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'pdf content'
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    with patch('builtins.open', mock_open()) as m:
        pdf_tool._download_pdf("http://example.com/file.pdf", "dummy_path")
        m.assert_called_once_with('dummy_path', 'wb')
        m().write.assert_called_once_with(b'pdf content')

@patch('requests.get')
def test_download_pdf_failure(mock_get):
    """Tests the _download_pdf helper function for a failed download."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = Exception("HTTP Error")
    mock_get.return_value = mock_response

    with pytest.raises(Exception):
        pdf_tool._download_pdf("http://example.com/file.pdf", "dummy_path")

@patch('fitz.open')
def test_extract_text_from_pdf(mock_fitz_open):
    """Tests the _extract_text_from_pdf helper function."""
    mock_page = MagicMock()
    mock_page.get_text.return_value = "page text"
    mock_doc = MagicMock()
    mock_doc.__iter__.return_value = [mock_page, mock_page]
    mock_fitz_open.return_value = mock_doc

    text = pdf_tool._extract_text_from_pdf("dummy_path")
    assert text == "page textpage text"

# Configure the mock for google.auth.default
mock_credentials = MagicMock()
mock_credentials.universe_domain = "googleapis.com"
@patch('google.auth.default', return_value=(mock_credentials, None))
@patch('tools.pdf_tool.GenerativeModel') # Patch where the object is looked up
def test_summarize_text_with_gemini(mock_gemini_model, mock_auth_default):
    """Tests the _summarize_text_with_gemini helper function."""
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value.text = "summary"
    mock_gemini_model.return_value = mock_model_instance

    summary = pdf_tool._summarize_text_with_gemini("long text")
    assert summary == "summary"

# --- Tests for Main Tool ---

@patch('tools.pdf_tool._extract_pdf_url', return_value=None)
def test_pdf_summary_tool_no_url(mock_extract):
    """Tests the main tool when no URL is found."""
    result = pdf_tool.pdf_summary_tool("a prompt")
    assert result == "No PDF link found in the prompt."

@patch('tools.pdf_tool._extract_pdf_url', return_value="http://example.com/file.pdf")
@patch('tools.pdf_tool._download_pdf', side_effect=Exception("Download failed"))
@patch('tempfile.NamedTemporaryFile')
def test_pdf_summary_tool_download_fails(mock_tempfile, mock_download, mock_extract):
    """Tests the main tool when the PDF download fails."""
    mock_tempfile.return_value.__enter__.return_value.name = "dummy_path"
    result = pdf_tool.pdf_summary_tool("a prompt")
    assert "An error occurred: Download failed" in result

@patch('tools.pdf_tool._extract_pdf_url', return_value="http://example.com/file.pdf")
@patch('tools.pdf_tool._download_pdf', return_value=None)
@patch('tools.pdf_tool._extract_text_from_pdf', return_value=" ")
@patch('tempfile.NamedTemporaryFile')
def test_pdf_summary_tool_no_text(mock_tempfile, mock_extract_text, mock_download, mock_extract):
    """Tests the main tool when no text can be extracted."""
    mock_tempfile.return_value.__enter__.return_value.name = "dummy_path"
    result = pdf_tool.pdf_summary_tool("a prompt")
    assert result == "Could not extract any text from the PDF."

@patch('tools.pdf_tool._extract_pdf_url', return_value="http://example.com/file.pdf")
@patch('tools.pdf_tool._download_pdf', return_value=None)
@patch('tools.pdf_tool._extract_text_from_pdf', return_value="some text")
@patch('tools.pdf_tool._summarize_text_with_gemini', return_value="the summary")
@patch('tempfile.NamedTemporaryFile')
def test_pdf_summary_tool_success(mock_tempfile, mock_summarize, mock_extract_text, mock_download, mock_extract):
    """Tests the main tool for a successful run."""
    mock_tempfile.return_value.__enter__.return_value.name = "dummy_path"
    result = pdf_tool.pdf_summary_tool("a prompt")
    assert result == "the summary"
