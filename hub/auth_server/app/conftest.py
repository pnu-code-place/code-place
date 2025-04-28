""" pytest configuration for the auth server. """
import os

# Mock the environment variables for testing
# This should be done before testing to ensure the app uses the mock values
os.environ["GITHUB_OAUTH_APP_ID"] = "test_app_id"
os.environ["GITHUB_OAUTH_APP_SECRET"] = "test_app_secret"
