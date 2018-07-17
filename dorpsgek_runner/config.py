import os

DORPSGEK_ADDRESS = os.environ["DORPSGEK_ADDRESS"]

ENVIRONMENT = os.environ["ENVIRONMENT"]
WORKING_FOLDER = os.getenv("WORKING_FOLDER", "/var/lib/dorpsgek-runner/workdir")

COMMANDS = os.getenv("COMMANDS", "")
