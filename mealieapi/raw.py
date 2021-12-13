import aiohttp
import json
import os
import re
import typing as t


def camel_to_snake_case(d: dict):
    for key, value in list(d.items()):
        new_key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
        d[new_key] = value
        del d[key]
        if isinstance(value, dict):
            d[new_key] = camel_to_snake_case(value)
    return d


class _RawClient:
    def __init__(self, url: str) -> None:
        self.url = url

    def endpoint(self, path: str) -> str:
        return os.path.join(self.url, 'api', path)

    def _headers(self) -> dict:
        return {
            "Accept": "application/json"
        }

    async def request(
        self,
        path: str,
        method: str = "GET",
        data: t.Union[dict, str] = None,
        params: dict = None,
        headers: dict = None,
        **kwargs
    ):
        if headers is None:
            headers = {}
        async with aiohttp.ClientSession(headers=self._headers()) as session:
            async with session.request(
                method=method,
                url=self.endpoint(path),
                data=json.dumps(data, indent=4),
                params=params,
                headers=headers,
                **kwargs
            ) as response:
                return await self.process_response(response)

    async def close(self) -> None:
        await self.session.close()

    async def process_response(self, response: aiohttp.ClientResponse):
        print('Request Response:', response.status)
        print(response.url)
        print(response.method)
        if 200 <= response.status < 300:
            if response.headers.get('Content-Type') == 'application/json':
                data = await response.json()
                if isinstance(data, dict) or isinstance(data, list):
                    data = camel_to_snake_case(data)
                print(json.dumps(data, indent=2))
                return data
            else:
                return await response.read()
        elif 400 <= response.status < 500:
            # TODO: Create Error handling system for json error responses
            raise ValueError(f"Status Code {response.status}: {await response.json()}")
        else:
            raise ValueError("Internal Server Error")
