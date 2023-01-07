from __future__ import annotations

from .auth import AccessTokenAuth, Auth, BasicAuth

from .models import AppInfo

from urllib.parse import urlparse


__all__ = ("Client",)


def scrub_url(url: str) -> str:
    parsed_url = urlparse(url)
    if parsed_url.scheme == "" or parsed_url.netloc == "":
        raise ValueError(f"Invalid URL: {url}")
    return parsed_url.geturl()


class Client(BasicAuth, AccessTokenAuth):
    session_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "mealieapi",
    }

    def __init__(
        self,
        url: str,
        api_key: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        if api_key is not None:
            AccessTokenAuth.__init__(self, scrub_url(url), api_key)
        elif username is not None and password is not None:
            BasicAuth.__init__(self, scrub_url(url), username, password)
        else:
            Auth.__init__(self, scrub_url(url))

    async def about(self) -> AppInfo:
        data = await self.request("GET", "api/app/about", use_auth=False)
        return AppInfo.parse_obj(data)
