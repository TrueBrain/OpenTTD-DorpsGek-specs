import itertools
import logging
import random

from collections import defaultdict

log = logging.getLogger(__name__)

_registry = defaultdict(list)
_runners = defaultdict(list)


async def process_request(event, ws):
    """
    Process a single request.
    """

    for func in _registry[event.type]:
        await func(event, ws)


def register(command):
    def wrapped(func):
        _registry[command].append(func)
        return func
    return wrapped


def add_runner(runner_ws, environment):
    log.info("New runner for %s", environment)
    _runners[environment].append(runner_ws)


def remove_runner(runner_ws):
    for env in _runners.keys():
        try:
            _runners[env].remove(runner_ws)
            log.info("Lost runner for %s", env)
        except ValueError:
            pass


def get_runner(*, environment=None):
    if environment:
        runners = _runners[environment]
    else:
        runners = list(itertools.chain.from_iterable(_runners.values()))

    return random.choice(runners)
