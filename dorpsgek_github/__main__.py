import logging
import http

from aiohttp import web

from dorpsgek_github import github
from dorpsgek_github.config import GITHUB_APP_PORT

# List of modules that are enabled
from dorpsgek_github.modules import (  # noqa
    ping,
    registration,
)


log = logging.getLogger(__name__)


async def github_handler(request):
    headers = request.headers
    data = await request.read()

    try:
        await github.process_request(headers, data)
        return web.Response(status=http.HTTPStatus.OK)
    except Exception:
        log.exception("Failed to handle GitHub event!")
        return web.Response(status=http.HTTPStatus.INTERNAL_SERVER_ERROR)


async def github_startup(app):
    await github.startup()


def main():
    app = web.Application()
    app.router.add_post("/", github_handler)
    app.on_startup.append(github_startup)

    web.run_app(app, port=GITHUB_APP_PORT)


if __name__ == "__main__":
    main()
