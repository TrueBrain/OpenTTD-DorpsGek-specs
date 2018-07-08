import os

GITHUB_APP_ID = os.environ["GITHUB_APP_ID"]
GITHUB_APP_SECRET = os.environ["GITHUB_APP_SECRET"]
GITHUB_APP_PORT = os.getenv("GITHUB_APP_PORT", 8080)

with open(os.environ["GITHUB_APP_PRIVATE_KEY_FILE"]) as f:
    GITHUB_APP_PRIVATE_KEY = f.read()
