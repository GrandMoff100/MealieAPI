import os
import aiohttp
import typing as t


class _RawClient:
    def __init__(self, url: str) -> None:
        self.url = url
        self.session = aiohttp.ClientSession()

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
        headers.update(self._headers())
        async with self.session as session:
            async with session.request(
                method=method,
                url=self.endpoint(path),
                data=data,
                params=params,
                headers=headers,
                **kwargs
            ) as response:
                return await self.process_response(response)

    async def close(self) -> None:
        pass

    async def process_response(self, response: aiohttp.ClientResponse):
        return await response.json()
        