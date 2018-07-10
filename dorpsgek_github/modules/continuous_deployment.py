import os
import tempfile

from dorpsgek_github.config import WORKING_FOLDER
from dorpsgek_github.helpers.dorpsgek_yml import parse_dorpsgek_yml
from dorpsgek_github.helpers.github import download_github_repository
from dorpsgek_github.processes.github import router as github


@github.register("push")
async def push(event, github_api):
    branch = event.data["ref"]
    ref = event.data["head_commit"]["id"]
    repository = event.data["repository"]["full_name"]
    clone_url = event.data["repository"]["clone_url"]

    assert branch.startswith("refs/heads/")
    branch = branch[len("refs/heads/"):]

    config = await parse_dorpsgek_yml(github_api, repository, ref)

    funcs_to_execute = []
    for stage, jobs in config.items():
        for job in jobs:
            if not job.is_valid_for(branch=branch):
                continue
            if job.is_manual():
                continue

            funcs_to_execute.append(job.get_coroutine())

    with tempfile.TemporaryDirectory("", "dorpsgek.%s." % repository.replace("/", "-"), WORKING_FOLDER) as work_folder:
        artifact_folder = f"{work_folder}/artifact"
        job_id = os.path.basename(work_folder)

        os.mkdir(artifact_folder)
        await download_github_repository(repository, ref, clone_url, work_folder)

        for func in funcs_to_execute:
            await func(job_id, repository, ref)
