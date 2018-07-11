from dorpsgek_github.yaml.exceptions import YAMLConfigurationError
from dorpsgek_github.yaml import registry as yaml


@yaml.register("environment")
def environment(job, data):
    """
    Set the environment for a job.

    This can be anything, as long as there is a runner running in the same environment.
    Normally this has values like 'testing', 'staging', and 'production'.
    """

    if not isinstance(data, dict) or "name" not in data:
        raise YAMLConfigurationError("no 'name' defined for 'environment'")

    job.set_environment(data["name"])
