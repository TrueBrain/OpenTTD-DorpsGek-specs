import os
import tempfile

from dorpsgek_github.config import WORKING_FOLDER
from dorpsgek_github.helpers.github import (
    download_repository,
    get_dorpsgek_yml,
)
from dorpsgek_github.processes.github import router as github
from dorpsgek_github.scheduler.context import Context
from dorpsgek_github.yaml.loader import load_yaml


@github.register("push")
async def push(event, github_api):
    branch = event.data["ref"]
    ref = event.data["head_commit"]["id"]
    repository = event.data["repository"]["full_name"]
    clone_url = event.data["repository"]["clone_url"]

    assert branch.startswith("refs/heads/")
    branch = branch[len("refs/heads/"):]

    raw_yml = await get_dorpsgek_yml(github_api, repository, ref)
    config = load_yaml(raw_yml)

    jobs_to_execute = []
    for stage, jobs in config.items():
        for job in jobs:
            if not job.match(branch=branch):
                continue
            if job.manual:
                continue

            jobs_to_execute.append(job)

    with tempfile.TemporaryDirectory("", "dorpsgek.%s." % repository.replace("/", "-"), WORKING_FOLDER) as work_folder:
        artifact_folder = f"{work_folder}/artifact"

        os.mkdir(artifact_folder)
        await download_repository(repository, ref, clone_url, work_folder)

        context = Context(repository_name=repository, ref=ref, artifact_folder=artifact_folder)

        for job in jobs_to_execute:
            await job.executor(job, context)
