import logging
import os
import typing as t

import aiohttp

from mealieapi.auth import Auth
from mealieapi.errors import MealieError
from mealieapi.misc import camel_to_snake_case


class _RawClient:
    auth: t.Optional[Auth] = None
    response_processors: t.Dict[str, t.Callable] = {}

    def __init__(self, url: str) -> None:
        self.url = url

    def endpoint(self, path: str) -> str:
        return os.path.join(self.url, "api", path)

    def _headers(self) -> dict:
        return {
            aiohttp.hdrs.ACCEPT: "application/json",
            aiohttp.hdrs.USER_AGENT: "MealieAPI-Python 0.0.0",
        }

    async def request(
        self,
        path: str,
        method: str = "GET",
        data: t.Union[str, None] = None,
        json: t.Union[dict, None] = None,
        params: t.Union[dict, None] = None,
        use_auth: bool = True,
        **kwargs,
    ) -> t.Any:
        headers = self._headers()
        if use_auth is False and self.auth is not None:
            del headers[aiohttp.hdrs.AUTHORIZATION]
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.request(
                method=method,
                url=self.endpoint(path),
                data=data,
                json=json,
                params=params,
                **kwargs,
            ) as response:
                return await self.process_response(response)

    @staticmethod
    def response_processor(mimetype: str) -> t.Callable:
        def register_processor(processor: t.Callable):
            _RawClient.response_processors[mimetype] = processor
            return processor

        return register_processor

    async def process_response(self, response: aiohttp.ClientResponse) -> t.Any:
        logging.debug(f"Status: {response.status}")
        logging.debug(f"URL: {response.url}")
        logging.debug(f"Method: {response.method}")
        logging.debug(f"Content: {await response.read()!r}"[:100] + "...")
        logging.debug(response.request_info)
        if 200 <= response.status < 300:

            async def default_handler(response: aiohttp.ClientResponse) -> bytes:
                return await response.read()

            content_type = response.headers.get(aiohttp.hdrs.CONTENT_TYPE)
            if content_type is not None:
                processor = self.response_processors.get(content_type, default_handler)
            else:
                raise MealieError("Mealie did not return a content-type header.")
            return await processor(response)
        elif 400 <= response.status < 500:
            # TODO: Create Error handling system for json error responses
            raise ValueError(f"Status Code {response.status}: {await response.json()}")
        else:
            raise ValueError("Internal Server Error")

    async def handle_error_json(self, data: dict):
        pass


@_RawClient.response_processor("application/json")
async def process_json(response: aiohttp.ClientResponse) -> t.Union[dict, str]:
    data = await response.json()
    if isinstance(data, dict) or isinstance(data, list):
        data = camel_to_snake_case(data)
    return data


@_RawClient.response_processor("application/octet-stream")
async def process_stream(response: aiohttp.ClientResponse) -> bytes:
    return await response.read()


class RawClient(_RawClient):
    def __init__(self, url) -> None:
        super().__init__(url)

    # Authorization
    def _headers(self) -> dict:
        """Updates the Raw Client headers with the Authorization header."""
        headers = super()._headers()
        if self.auth is not None:
            headers.update(self.auth.header)
        return headers

    async def _get_token(self, username: str, password: str) -> Auth:
        """Exchanges the login credentials of a user for a temporary API token."""
        data = await self.request(
            "auth/token",
            method="POST",
            data={"username": username, "password": password},  # type: ignore[arg-type]
            use_auth=False,
        )
        return Auth(self, **data)

    async def login(self, username: str, password: str) -> None:
        """Makes the Client authorize with the login credentials of a user."""
        self.auth = await self._get_token(username, password)

    def authorize(self, token: str) -> None:
        """Makes the Client authorize with an API token."""
        self.auth = Auth(self, token)
