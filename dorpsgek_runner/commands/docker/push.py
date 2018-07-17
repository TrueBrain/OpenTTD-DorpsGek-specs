from dorpsgek_runner import runner


@runner.register("docker.push")
async def docker_push(event, ws):
    print(event.data)
