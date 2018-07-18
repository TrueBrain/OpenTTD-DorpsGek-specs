import os

from dorpsgek_runner.helpers.subprocess import CommandError
from dorpsgek_runner import (
    config,
    runner,
)
from dorpsgek_runner.helpers.subprocess import run_command


class DockerRunNotConfiguredForDeployment(Exception):
    """Thrown if the repository is not configured for deployment on the environment."""


@runner.register("docker.run")
async def docker_run(event, ws):
    repository_name_lowercase = event.data["name"].lower()
    container_name = event.data["name"].replace("/", "_").lower()
    image_name = f"{event.data['name']}:{event.data['tag']}".lower()

    deployment_folder = f"{config.DEPLOYMENT_CONFIG_FOLDER}/{config.ENVIRONMENT}/{repository_name_lowercase}/"
    deployment_file = f"{deployment_folder}/deployment.yml"
    deployment_private_file = f"{deployment_folder}/deployment-private.yml"

    if not os.path.isfile(deployment_file):
        raise DockerRunNotConfiguredForDeployment(config.ENVIRONMENT)

    if os.path.isfile(deployment_private_file):
        pass

    # TODO -- Process deployment files, extending the run command

    # Shut down the possibly already running docker instance
    try:
        await run_command(f"docker container inspect {container_name}")
    except CommandError as err:
        # We expect errorcode 1, assuming that means: no such container
        if err.args[0] != 1:
            raise
    else:
        await run_command(f"docker stop {container_name}")

    await run_command(f"docker run -d --rm --name {container_name} {image_name}")
