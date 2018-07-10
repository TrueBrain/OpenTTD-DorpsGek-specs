import base64
import gidgethub
import yaml

from dorpsgek_github.scheduler.job import (
    Job,
    JobError,
)


RESERVED_JOB_WORDS = ["stages"]
RESERVED_CONFIG_WORDS = ["stage"]


class DorpsGekYMLParseError(Exception):
    pass


async def get_dorpsgek_yml(github_api, repository, ref):
    try:
        response = await github_api.getitem(f"/repos/{repository}/contents/.dorpsgek.yml?ref={ref}")
    except gidgethub.BadRequest as err:
        if err.args != ("Not Found",):
            raise

        # No .dorpsgek.yml in this repository; so nothing to do!
        return

    return base64.b64decode(response["content"])


async def parse_dorpsgek_yml(github_api, repository, ref):
    raw_yml = await get_dorpsgek_yml(github_api, repository, ref)
    if raw_yml is None:
        return

    configuration = yaml.load(raw_yml)
    errors = []

    stages = configuration.get("stages", ["test", "build", "deploy"])
    jobs = {stage: [] for stage in stages}

    for job_name, job_config in configuration.items():
        if job_name in RESERVED_JOB_WORDS:
            continue

        job = Job(job_name)

        for config, data in job_config.items():
            if config in RESERVED_CONFIG_WORDS:
                continue

            func = getattr(job, f"handle_{config}", None)
            if func is not None:
                try:
                    func(data)
                except JobError as err:
                    errors.append(err.args)
            else:
                errors.append(f"unexpected '{config}' in job '{job_name}'")
                continue

        if "stage" not in job_config:
            errors.append(f"no 'stage' defined for job '{job_name}'")
        else:
            jobs[job_config["stage"]].append(job)

    if errors:
        raise DorpsGekYMLParseError(errors)

    return jobs
