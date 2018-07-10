import os

from dorpsgek_github.config import WORKING_FOLDER
from dorpsgek_github.processes.runner import get_runner


ONLY_SUPPORTED = ["branches", "tags"]
ONLY_NOT_SUPPORTED = ["api", "external", "pipelines", "pushes", "schedules", "triggers", "web"]


class JobError(Exception):
    pass


class Job:
    def __init__(self, name):
        self._name = name
        self._only = []
        self._when = None
        self._dorpsgek = None
        self._environment = None

    def handle_only(self, data):
        if not isinstance(data, list):
            data = [data]

        for entry in data:
            # We do not support (yet) the following entries
            if entry in ONLY_NOT_SUPPORTED:
                raise JobError(f"'{entry}' is  not supported (yet) for 'only' in job '{self._name}'")
            if "@" in entry:
                raise JobError(f"paths are  not supported (yet) for 'only' in job '{self._name}'")

        self._only = data

    def handle_when(self, data):
        self._when = data

    def handle_dorpsgek(self, data):
        self._dorpsgek = data

    def handle_environment(self, data):
        if "name" not in data:
            raise JobError(f"no 'name' defined for 'environment' in job '{self._name}'")
        self._environment = data["name"]

    def __repr__(self):
        return f"<Job name:{self._name}>"

    def is_valid_for(self, *, branch=None, tag=None):
        if not self._only:
            return True

        for entry in self._only:
            if branch is not None:
                if entry == "branches":
                    break
                if entry in ONLY_SUPPORTED:
                    continue

                regex_value = branch

            elif tag is not None:
                if entry == "tags":
                    break
                if entry in ONLY_SUPPORTED:
                    continue

                regex_value = tag
            else:
                continue

            # TODO - Support regex
            if entry == regex_value:
                break
            continue
        else:
            return False
        return True

    def is_manual(self):
        return self._when == "manual"

    def get_coroutine(self):
        if self._dorpsgek == "build":
            return self.task_dorpsgek_build
        if self._dorpsgek == "deploy":
            return self.task_dorpsgek_deploy

        raise JobError(f"no clue how to execute the job '{self._name}'")

    async def task_dorpsgek_build(self, job_id, repository, ref):
        runner_ws = get_runner(environment="build")

        source_filename = f"{WORKING_FOLDER}/{job_id}/artifact/source.tar.gz"
        source_filesize = os.stat(source_filename).st_size

        await runner_ws.send_request("job.start")
        await runner_ws.send_request("artifact.download", {
            "name": "source",
            "size": source_filesize,
        })

        # Send file in chunks of 1 KiB
        with open(source_filename, "rb") as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                await runner_ws.send_bytes(data)

        await runner_ws.send_request("docker.build", {
            "name": repository,
            "tag": ref,
        })
        await runner_ws.send_request("job.done")

    async def task_dorpsgek_deploy(self, job_id, repository, ref):
        runner_ws = get_runner(environment=self._environment)

        await runner_ws.send_request("job.start")
        await runner_ws.send_request("docker.pull", {
            "name": repository,
            "ref": ref,
        })
        await runner_ws.send_request("docker.run", {
            "name": repository,
            "ref": ref,
        })
        await runner_ws.send_request("job.done")
