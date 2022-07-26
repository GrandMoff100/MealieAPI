import logging
import posixpath
import typing as t

import aiohttp

from mealieapi.auth import Auth
from mealieapi.errors import (
    BadRequestError,
    InternalServerError,
    MealieError,
    ParameterMissingError,
    UnauthenticatedError,
)
from mealieapi.misc import camel_to_snake_case

_LOGGER = logging.getLogger(__name__)


class _RawClient:
    auth: Auth | None = None
    response_processors: dict[str, t.Callable] = {}

    def __init__(self, url: str) -> None:
        self.url = url

    def endpoint(self, path: str) -> str:
        return posixpath.join(self.url, "api", path)

    def _headers(self) -> dict[str, str]:
        return {
            aiohttp.hdrs.ACCEPT: "application/json",
            aiohttp.hdrs.USER_AGENT: "MealieAPI-Python 0.0.0",
        }

    async def request(
        self,
        path: str,
        method: str = "GET",
        data: str | None = None,
        json: dict[str, t.Any] | None = None,
        params: dict[str, t.Any] | None = None,
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
        _LOGGER.debug("Status: %i", response.status)
        _LOGGER.debug("URL: %s", response.url)
        _LOGGER.debug("Method: %r", response.method)
        _LOGGER.debug("Content: %r ", (await response.read())[:100] + b"...")
        _LOGGER.debug(response.request_info)

        if 200 <= response.status < 300:

            async def default_handler(response: aiohttp.ClientResponse) -> bytes:
                return await response.read()

            content_type = response.headers.get(aiohttp.hdrs.CONTENT_TYPE)
            if content_type is None:
                raise MealieError("Mealie did not return a content-type header.")
            processor = self.response_processors.get(content_type, default_handler)
            return await processor(response)
        if 400 <= response.status < 500:
            await self.handle_error_json(await response.json())
        else:
            raise InternalServerError("Mealie had a problem with your request.")

    async def handle_error_json(self, data: dict) -> None:
        if detail := data.get("detail", "Bad Request") == "Not authenticated":
            raise UnauthenticatedError("Not authenticated with Mealie")
        if detail == "Bad Request":
            raise BadRequestError("Error with your request.")
        if detail == "Internal Server Error":
            raise InternalServerError()
        if isinstance(detail, list):
            for error in detail:
                if error["type"] == "value_error.missing":
                    params = error["loc"]
                    msg = error["msg"]
                    raise ParameterMissingError(
                        f"Missing the parameters {params!r}, {msg}"
                    )


@_RawClient.response_processor("application/json")
async def process_json(response: aiohttp.ClientResponse) -> dict[str, t.Any] | str:
    data = await response.json()
    if isinstance(data, (dict, list)):
        data = camel_to_snake_case(data)
    return data


@_RawClient.response_processor("application/octet-stream")
async def process_stream(response: aiohttp.ClientResponse) -> bytes:
    return await response.read()


class RawClient(_RawClient):
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
        return Auth(_client=self, **data)  # type: ignore[arg-type]

    async def login(self, username: str, password: str) -> None:
        """Makes the Client authorize with the login credentials of a user."""
        self.auth = await self._get_token(username, password)

    def authorize(self, token: str) -> None:
        """Makes the Client authorize with an API token."""
        self.auth = Auth(_client=self, token=token)  # type: ignore[arg-type]
