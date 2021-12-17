import aiohttp
import json
import logging
import os
import re
import typing as t


JSONObject = t.Union[list, t.Union[dict, str]]


def camel_to_snake_case(obj: JSONObject):
    if isinstance(obj, dict):
        for key, value in list(obj.items()):
            new_key = camel_to_snake_case(key)
            del obj[key]
            obj[new_key] = value
            if isinstance(value, dict):
                obj[new_key] = camel_to_snake_case(value)
        return obj
    elif isinstance(obj, list):
        return [camel_to_snake_case(item) for item in obj]
    elif isinstance(obj, str):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', obj).lower()


class _RawClient:
    response_processors = {}

    def __init__(self, url: str) -> None:
        self.url = url

    def endpoint(self, path: str) -> str:
        return os.path.join(self.url, 'api', path)

    def _headers(self) -> dict:
        return {
            aiohttp.hdrs.ACCEPT: "application/json",
            aiohttp.hdrs.USER_AGENT: "MealieAPI-Python 0.0.0"
        }

    async def request(
        self,
        path: str,
        method: str = "GET",
        data: str = None,
        json: dict = None,
        params: dict = None,
        use_auth: bool = True,
        **kwargs
    ):
        headers = self._headers()
        if use_auth is False:
            del headers[aiohttp.hdrs.AUTHORIZATION]
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.request(
                method=method,
                url=self.endpoint(path),
                data=data,
                json=json,
                params=params,
                **kwargs
            ) as response:
                return await self.process_response(response)

    @staticmethod
    def response_processor(mimetype: str):
        def register_processor(processor: t.Callable):
            _RawClient.response_processors[mimetype] = processor
            return processor
        return register_processor

    async def process_response(self, response: aiohttp.ClientResponse) -> t.Any:
        logging.debug(f'Status: {response.status}')
        logging.debug(f'URL: {response.url}')
        logging.debug(f'Method: {response.method}')
        logging.debug(f'Content: {await response.read()}'[:100] + '...')
        logging.debug(response.request_info)
        if 200 <= response.status < 300:
            async def default_handler(response: aiohttp.ClientResponse) -> bytes:
                return await response.read()
            content_type = response.headers.get(aiohttp.hdrs.CONTENT_TYPE)
            processor = self.response_processors.get(content_type, default_handler)
            return await processor(response)

        elif 400 <= response.status < 500:
            # TODO: Create Error handling system for json error responses
            raise ValueError(f"Status Code {response.status}: {await response.json()}")

        else:
            raise ValueError("Internal Server Error")

    async def handle_error_json(self, data: dict):
        pass


@_RawClient.response_processor('application/json')
async def process_json(response: aiohttp.ClientResponse) -> t.Union[dict, str]:
    data = await response.json()
    if isinstance(data, dict) or isinstance(data, list):
        data = camel_to_snake_case(data)
    return data


@_RawClient.response_processor("application/octet-stream")
async def process_stream(response: aiohttp.ClientResponse):
    pass



