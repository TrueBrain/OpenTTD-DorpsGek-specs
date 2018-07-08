from dorpsgek_github.github import (
    add_installation,
    remove_installation,
    router as github,
)


@github.register("installation", action="created")
async def installation_created(event, github_api):
    add_installation(event.data["installation"]["id"])


@github.register("installation", action="deleted")
async def installation_deleted(event, github_api):
    remove_installation(event.data["installation"]["id"])


@github.register("installation_repositories", action="added")
async def installation_repositories_added(event, github_api):
    # Placeholder to have all relevant endpoints already defined.
    # Currently we don't track the exact repository we have access to, so no need to do anything.
    pass


@github.register("installation_repositories", action="removed")
async def installation_repositories_removed(event, github_api):
    # Placeholder to have all relevant endpoints already defined
    # Currently we don't track the exact repository we have access to, so no need to do anything.
    pass
