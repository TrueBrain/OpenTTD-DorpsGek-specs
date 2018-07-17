import aiohttp
import datetime
import logging
import jwt
import time

from gidgethub import (
    routing,
    sansio,
)
from gidgethub.aiohttp import GitHubAPI
from gidgethub.sansio import accept_format

from dorpsgek_github.config import (
    GITHUB_APP_ID,
    GITHUB_APP_PRIVATE_KEY,
    GITHUB_APP_SECRET,
)

log = logging.getLogger(__name__)
router = routing.Router()
_github_tokens = {}
_github_installations = {}


# HACK - Monkeypatch a fix that is already upstream:
# https://github.com/brettcannon/gidgethub/commit/9f3700db8a62ca3aa229c8291a40b50845dfb12d
# Should be part of 3.0.0
@classmethod
def ratelimit_from_http(cls, headers):
    try:
        limit = int(headers["x-ratelimit-limit"])
        remaining = int(headers["x-ratelimit-remaining"])
        reset_epoch = float(headers["x-ratelimit-reset"])
    except KeyError:
        return None
    else:
        return cls(limit=limit, remaining=remaining, reset_epoch=reset_epoch)
sansio.RateLimit.from_http = ratelimit_from_http  # noqa


class MyGitHubAPI(GitHubAPI):
    def __init__(self, session, *args, **kwargs):
        self._jwt = None
        super().__init__(session, *args, **kwargs)

    async def _request(self, method, url, headers, body=b""):
        if self._jwt:
            headers["authorization"] = f"Bearer {self._jwt}"
        if self._oauth_token:
            headers["authorization"] = f"token {self._oauth_token}"
        self._jwt = None
        self._oauth_token = None

        return await super()._request(method, url, headers, body)

    async def getitem(self, url, url_vars={}, *, accept=sansio.accept_format(), jwt=None, oauth_token=None):
        # HACK - support jwt authorization; https://github.com/brettcannon/gidgethub/pull/62 fixes this correctly.
        # While waiting for that to land, keep the API the same, and adopt the functionality.
        self._jwt = jwt
        self._oauth_token = oauth_token

        return await super().getitem(url, url_vars, accept=accept)

    async def post(self, url, url_vars={}, *, data, accept=sansio.accept_format(), jwt=None, oauth_token=None):
        # HACK - support jwt authorization; https://github.com/brettcannon/gidgethub/pull/62 fixes this correctly.
        # While waiting for that to land, keep the API the same, and adopt the functionality.
        self._jwt = jwt
        self._oauth_token = oauth_token

        return await super().post(url, url_vars, data=data, accept=accept)


class GitHubAPIContext:
    """
    Contextmanager to make GitHub API access a bit easier.

    It automatically creates a new ClientSession, and sets a generic UserAgent to all GitHub API calls.

    ClientSession is released to the pool on exit.
    """

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return MyGitHubAPI(self._session, "DorpsGek/0.1")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.close()


async def process_request(headers, data):
    """
    Process a single request.

    This is a very minimal wrapper to the Router dispatcher.
    """

    event = sansio.Event.from_http(headers, data, secret=GITHUB_APP_SECRET)

    async with GitHubAPIContext() as github_api:
        await router.dispatch(event, github_api)


async def get_oauth_token(installation_id):
    """
    Get the oauth_token for a given installation_id.

    It first checks if the oauth_token is in the cache and still valid. Otherwise it will retrieve a new
    token from the server.

    Tokens that are about to expire (give or take 5 minutes) are considered expired, to reduce the amount of
    possible 401s given.
    """

    if _github_installations[installation_id] is not None:
        expires_at, oauth_token = _github_installations[installation_id]
        if expires_at > datetime.datetime.now() + datetime.timedelta(minutes=5):
            return oauth_token

    async with GitHubAPIContext() as github_api:
        data = await github_api.post(f"/installations/{installation_id}/access_tokens",
                                     data="",
                                     accept=accept_format(version="machine-man-preview"),
                                     jwt=get_jwt())

        expires_at = datetime.datetime.strptime(data["expires_at"], "%Y-%m-%dT%H:%M:%SZ")
        _github_installations[installation_id] = (expires_at, data["token"])


async def startup():
    """
    On startup do some initial requests to GitHub API.

    This has two purposes:
     - It lists our installations, allowing us to check if we are still in sync over time (in regards to installations)
     - Check if our JWT it valid to communicate with GitHub API.
    """

    async with GitHubAPIContext() as github_api:
        installations = await github_api.getitem("/app/installations",
                                                 accept=accept_format(version="machine-man-preview"),
                                                 jwt=get_jwt())
        for installation in installations:
            _github_installations[installation["id"]] = None

    log.info("Startup done; found %d installations", len(_github_installations))


def get_jwt():
    """
    Get the JWT token that is valid for the GitHub API.
    """

    now = int(time.time())

    # The JWT is only valid for one minute; we often only do a single action with them, so the shorter the better.
    # This does mean the server needs to be NTP sync'd (or not drift more than a minute).
    data = {
        "iat": now,
        "exp": now + 60,
        "iss": GITHUB_APP_ID,
    }

    return jwt.encode(data, key=GITHUB_APP_PRIVATE_KEY, algorithm="RS256").decode()


def add_installation(installation_id):
    """
    Add a known installation identifier to the system.
    """

    if installation_id in _github_installations:
        raise Exception(f"Installation {installation_id} already known")
    _github_installations[installation_id] = None


def remove_installation(installation_id):
    """
    Remove an installation identifier from the system.
    """

    del _github_installations[installation_id]
