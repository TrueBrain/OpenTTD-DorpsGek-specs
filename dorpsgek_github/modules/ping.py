from dorpsgek_github.github import router as github


@github.register("ping")
async def ping(event, github_api):
    # By simply doing nothing, we will return an OK on the ping.
    # This is all GitHub would like to see. No further action needed.
    pass
