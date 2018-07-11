import os

REFERENCE_REPOSITORY_FOLDER = os.getenv("REFERENCE_REPOSITORY_FOLDER", "/var/lib/dorpsgek/reference")
if not os.path.exists(REFERENCE_REPOSITORY_FOLDER):
    os.mkdir(REFERENCE_REPOSITORY_FOLDER)
WORKING_FOLDER = os.getenv("WORKING_FOLDER", "/var/lib/dorpsgek/workdir")
if not os.path.exists(WORKING_FOLDER):
    os.mkdir(WORKING_FOLDER)

GITHUB_APP_ID = os.environ["GITHUB_APP_ID"]
GITHUB_APP_SECRET = os.environ["GITHUB_APP_SECRET"]
GITHUB_APP_PORT = os.getenv("GITHUB_APP_PORT", 8080)
with open(os.environ["GITHUB_APP_PRIVATE_KEY_FILE"]) as f:
    GITHUB_APP_PRIVATE_KEY = f.read()

RUNNER_PORT = os.getenv("RUNNER_PORT", 8081)
