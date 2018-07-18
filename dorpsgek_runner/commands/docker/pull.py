from dorpsgek_runner import runner


@runner.register("docker.pull")
async def docker_pull(event, ws):
    print(event.data)
