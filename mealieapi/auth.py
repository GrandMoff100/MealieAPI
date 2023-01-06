import json
from posixpath import join as urljoin
from typing import Any, cast

from aiohttp import ClientSession


class Auth(ClientSession):
    REFRESH_AFTER: int = 60 * 60 * 12

    def __init__(
        self,
        url: str,
        access_token: str | None = None,
        token_type: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._api = url
        self._access_token: str | None = access_token
        self._token_type: str | None = token_type
        super().__init__(*args, **kwargs, headers=self.session_headers)

    async def _headers(self) -> dict[str, str]:
        print(self._access_token)
        if self._access_token is not None:
            return {
                "Authorization": f"{self._token_type.capitalize()} {self._access_token}"
            }
        return {}

    async def request(
        self,
        method: str,
        endpoint: str,
        headers: dict[str, str] | None = None,
        use_auth: bool = True,
        params: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any] | bytes:
        """Make a request to the API with proper authentication."""
        _headers = {} if not use_auth else await self._headers()
        response = await ClientSession.request(
            self,
            method,
            urljoin(self._api, endpoint),
            headers=_headers | (headers or {}),
            params=params,
            **kwargs,
        )
        if response.content_type == "application/json":
            return await response.json()
        if response.content_type == "text/html":
            raise UserWarning("Did you request the wrong endpoint? The response was HTML.")
        if response.content_type.startswith("text/"):
            return await response.text()
        return await response.content.read()

    async def get_token(
        self,
        username: str,
        password: str,
        grant_type: str | None = None,
        scope: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        long_term: bool = False,
    ) -> dict[str, str]:
        """Get a session token from the API."""
        data = await self.request(
            method="POST",
            endpoint="api/auth/token",
            data={
                "username": username,
                "password": password,
                "grant_type": grant_type if grant_type is not None else "password",
                "scope": scope if scope is not None else "",
                "client_id": client_id if client_id is not None else "",
                "client_secret": client_secret if client_secret is not None else "",
                "remember_me": "true" if long_term else "false",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            use_auth=False,
        )
        return cast(dict[str, str], data)


class AccessTokenAuth(Auth):
    def __init__(
        self, url: str, access_token: str | None, token_type: str = "bearer"
    ) -> None:
        super().__init__(url, access_token, token_type)


class BasicAuth(Auth):
    def __init__(self, url: str, username: str, password: str) -> None:
        self._username = username
        self._password = password
        super().__init__(url, None)

    async def _headers(self) -> dict[str, str]:
        if self._access_token is None:
            data = await self.get_token(self._username, self._password)
            print(data)
            self._access_token = data.get("access_token")
            self._token_type = data.get("token_type")
        return await super()._headers()
