import os
import tempfile

from dorpsgek_runner import runner
from dorpsgek_runner.config import WORKING_FOLDER


@runner.register("job.start")
async def job_start(event, ws):
    ws.tempdir = tempfile.TemporaryDirectory("", "runner.", WORKING_FOLDER)
    os.mkdir(f"{ws.tempdir.name}/artifact")


@runner.register("job.done")
async def job_done(event, ws):
    ws.tempdir.cleanup()
    ws.tempdir = None
