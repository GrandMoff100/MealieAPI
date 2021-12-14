import aiohttp
import os
import re
import typing as t


def camel_to_snake_case(d: dict):
    for key, value in list(d.items()):
        new_key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
        del d[key]
        d[new_key] = value
        if isinstance(value, dict):
            d[new_key] = camel_to_snake_case(value)
    return d


class _RawClient:
    response_processors = {}

    def __init__(self, url: str) -> None:
        self.url = url

    def endpoint(self, path: str) -> str:
        return os.path.join(self.url, 'api', path)

    def _headers(self) -> dict:
        return {
            "Accept": "application/json",
            "User-Agent": "MealieAPI-Python 0.0.0"
        }

    async def request(
        self,
        path: str,
        method: str = "GET",
        data: t.Union[dict, str] = None,
        params: dict = None,
        headers: dict = None,
        use_auth: bool = True,
        **kwargs
    ):
        if headers is None:
            headers = {}
        headers.update(self._headers())
        if use_auth is False:
            del headers['Authorization']

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.request(
                method=method,
                url=self.endpoint(path),
                data=data,
                params=params,
                headers=headers,
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
        print('Status:', response.status)
        print('URL:', response.url)
        print('Method:', response.method)
        print('Content:', await response.read())
        if 200 <= response.status < 300:
            def default_handler(response: aiohttp.ClientResponse) -> bytes:
                return await response.read()
            content_type = response.headers.get('Content-Type')
            processor = self.response_processors.get(content_type, default_handler)
            return processor(response)

        elif 400 <= response.status < 500:
            # TODO: Create Error handling system for json error responses
            raise ValueError(f"Status Code {response.status}: {await response.json()}")

        else:
            raise ValueError("Internal Server Error")

    async def handle_error_json(self, data: dict):
        pass


@_RawClient.response_processor('application/json')
def process_json(self, response: aiohttp.ClientResponse) -> t.Union[dict, str]:
    data = await response.json()
    if isinstance(data, dict) or isinstance(data, list):
        data = camel_to_snake_case(data)
    return data


@_RawClient.response_processor("application/octet-stream")
def process_stream(self, response: aiohttp.ClientResponse):
    pass



