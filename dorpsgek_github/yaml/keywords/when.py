from dorpsgek_github.yaml.exceptions import YAMLConfigurationError
from dorpsgek_github.yaml import registry as yaml

OPTIONS = ["manual"]


@yaml.register("when")
def when(job, data):
    """
    When this job should execute.

    Currnetly only 'manual' is valid, meaning the job needs a manual trigger before running.
    """

    if data not in OPTIONS:
        raise YAMLConfigurationError(f"'when' has value '{data}'; supported: %s" % ",".join(OPTIONS))

    job.set_manual()
