import http
import logging

from aiohttp import web
from dorpsgek_github.processes import github

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
