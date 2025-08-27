import os

# Set dummy environment variables before any tests are run.
# This is necessary because the tool modules check for these variables
# at import time, which happens before pytest fixtures can be applied.
# By setting them here in conftest.py, we ensure they exist when
# pytest imports the test files and their dependencies.
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["SLACK_WEBHOOK_URL"] = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
