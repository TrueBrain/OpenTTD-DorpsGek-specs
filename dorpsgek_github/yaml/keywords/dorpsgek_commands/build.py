import os

from dorpsgek_github.processes.runner import get_runner
from dorpsgek_github.yaml.keywords import dorpsgek


@dorpsgek.register("build")
async def build(job, context):
    """
    Create a container which can be deployed.

    This requires a valid Dockerfile in the root of the repository.
    """

    runner_ws = get_runner(environment=job.environment)

    source_filename = f"{context.artifact_folder}/source.tar.gz"
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
        "name": context.repository_name,
        "tag": context.ref,
    })
    await runner_ws.send_request("job.done")
