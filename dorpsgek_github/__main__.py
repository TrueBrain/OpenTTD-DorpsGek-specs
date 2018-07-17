import asyncio
import logging

from aiohttp import web

from dorpsgek_github.helpers.aiohttp_web import (
    prepare_app,
    run_apps,
)
from dorpsgek_github.aiohttp_apps.github import (
    github_handler,
    github_startup,
)
from dorpsgek_github.aiohttp_apps.runner import runner_handler
from dorpsgek_github.config import (
    GITHUB_APP_PORT,
    RUNNER_PORT,
)
from dorpsgek_github.scheduler.scheduler import schedule_runner

# List of modules that are enabled
from dorpsgek_github.modules import (  # noqa
    continuous_deployment,
    ping,
    registration,
)

log = logging.getLogger(__name__)


def create_web_apps():
    apps = []

    github_app = web.Application()
    github_app.router.add_post("/", github_handler)
    github_app.on_startup.append(github_startup)
    apps.append(prepare_app(github_app, port=GITHUB_APP_PORT))

    runner_app = web.Application()
    runner_app.router.add_get("/", runner_handler)
    apps.append(prepare_app(runner_app, port=RUNNER_PORT))

    return apps


def main():
    logging.basicConfig(level=logging.INFO)

    apps = create_web_apps()

    asyncio.ensure_future(schedule_runner())
    run_apps(apps, print=log.info)


if __name__ == "__main__":
    main()
