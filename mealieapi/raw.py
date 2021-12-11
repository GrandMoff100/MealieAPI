import os
import aiohttp


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
        json: dict = None,
        params: dict = None,
        headers: dict = None,
        **kwargs
    ):
        if headers is None:
            headers = {}
        if json is None:
            json = {}
        if params is None:
            params = {}
        headers.update(self.headers())
        with self.session as session:
            async with session.request(
                self.endpoint(path),
                method=method,
                json=json,
                params=params,
                **kwargs
            )

    async def close(self) -> None:
        pass

    async def process_response(self, response: aiohttp.Response):
        pass