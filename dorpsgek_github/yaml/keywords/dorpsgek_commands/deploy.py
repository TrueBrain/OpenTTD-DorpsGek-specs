from dorpsgek_github.processes.runner import get_runner
from dorpsgek_github.yaml.keywords import dorpsgek


@dorpsgek.register("deploy")
async def deploy(job, context):
    """Deploy a container to an environment."""

    runner_ws = get_runner(environment=job.environment)

    await runner_ws.send_request("job.start")
    await runner_ws.send_request("docker.pull", {
        "name": context.repository_name,
        "tag": context.ref,
    })
    await runner_ws.send_request("docker.run", {
        "name": context.repository_name,
        "tag": context.ref,
    })
    await runner_ws.send_request("job.done")
