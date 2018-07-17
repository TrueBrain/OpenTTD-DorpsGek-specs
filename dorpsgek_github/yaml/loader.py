import yaml

from dorpsgek_github.scheduler.job import Job
from dorpsgek_github.yaml.exceptions import (
    YAMLConfigurationError,
    YAMLConfigurationErrors,
)
from dorpsgek_github.yaml.registry import get_keyword_handler

# Load the available keywords
from dorpsgek_github.yaml.keywords import (  # noqa
    dorpsgek,
    environment,
    only,
    when,
)

# Load the available dorpsgek commands
from dorpsgek_github.yaml.dorpsgek_commands import (  # noqa
    build,
    deploy,
)


RESERVED_JOB_WORDS = ["stages"]
RESERVED_CONFIG_WORDS = ["stage"]


def load_yaml(raw_yml):
    """Load a YAML file assuming it represents a DorpsGek YAML configuration file."""

    if not raw_yml:
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

            func = get_keyword_handler(config)
            if func:
                try:
                    func(job, data)
                except YAMLConfigurationError as err:
                    errors.append(f"{err.args} in job '{job_name}'")

            else:
                errors.append(f"unexpected '{config}' in job '{job_name}'")
                continue

        if not job.is_valid():
            errors.append(f"job '{job_name}' is not a valid job")

        if "stage" not in job_config:
            errors.append(f"no 'stage' defined for job '{job_name}'")
        else:
            jobs[job_config["stage"]].append(job)

    if errors:
        raise YAMLConfigurationErrors(errors)

    return jobs
