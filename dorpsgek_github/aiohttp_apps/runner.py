import logging

from aiohttp import (
    web,
    WSMsgType,
)
from asyncio import CancelledError, Queue
from dorpsgek_github.processes import runner

log = logging.getLogger(__name__)


class RunnerEvent:
    def __init__(self, type, data=None):
        self.type = type
        self.data = data


async def runner_send_event(self, event, data=None):
    payload = {
        "type": event,
    }
    if data:
        payload["data"] = data

    await self.send_json(payload)
web.WebSocketResponse.send_event = runner_send_event  # noqa


async def runner_send_request(self, event, data=None):
    payload = {
        "type": event,
    }
    if data:
        payload["data"] = data

    await self.send_event("request", payload)
    return await self.request_response_queue.get()
web.WebSocketResponse.send_request = runner_send_request  # noqa


RUNNER_CLOSE_EVENT = RunnerEvent("close")


async def runner_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    ws.request_response_queue = Queue(maxsize=1)
    await ws.send_event("welcome")

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                raw = msg.json()
                event = RunnerEvent(raw["type"], raw.get("data"))

                if event.type == "response":
                    await ws.request_response_queue.put(event.data.get("data"))
                else:
                    await runner.process_request(event, ws)
            elif msg.type == WSMsgType.ERROR:
                log.error("Runner connection closed with exception", ws.exception())
                await runner.process_request(RUNNER_CLOSE_EVENT, ws)
                break
            else:
                log.error(f"Unexpected type {msg.type}")
                break
    except CancelledError:
        # This is the other side terminating the connection
        await runner.process_request(RUNNER_CLOSE_EVENT, ws)
    except Exception:
        log.exception("Failed to handle runner event!")
        await runner.process_request(RUNNER_CLOSE_EVENT, ws)

    return ws
