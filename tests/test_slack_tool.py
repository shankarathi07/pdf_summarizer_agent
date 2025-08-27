import pytest
import requests
from tools import slack_tool

def test_slack_notifier_tool_success(mocker):
    """
    Tests that the slack_notifier_tool returns a success message
    when the request is successful.
    """
    # Mock the requests.post call to return a successful response
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.status_code = 200
    mock_post.return_value.raise_for_status.return_value = None

    # Call the tool
    result = slack_tool.slack_notifier_tool("Test message")

    # Assert that the tool returns the success message
    assert result == "Posted to Slack"

def test_slack_notifier_tool_failure(mocker):
    """
    Tests that the slack_notifier_tool returns an error message
    when the request fails.
    """
    # Mock the requests.post call to raise a RequestException
    mock_post = mocker.patch('requests.post')
    mock_post.side_effect = requests.exceptions.RequestException("Test error")

    # Call the tool
    result = slack_tool.slack_notifier_tool("Test message")

    # Assert that the tool returns the error message
    assert "Slack error: Test error" in result
