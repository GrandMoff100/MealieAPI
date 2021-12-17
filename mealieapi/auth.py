import aiohttp
from dataclasses import dataclass


@dataclass()
class Auth:
    _client: "MealieClient"
    access_token: str
    token_type: str = None

    async def refresh(self):
        resp = await self._client.request("auth/refresh")
        self.access_token = resp['access_token']
        self.token_type = resp['token_type']

    @property
    def header(self):
        return {
            aiohttp.hdrs.AUTHORIZATION: f"Bearer {self.access_token}"
        }
