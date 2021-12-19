import typing as t
from dataclasses import dataclass, field

import aiohttp

from mealieapi.mixins import JsonModel

if t.TYPE_CHECKING:
    from mealieapi.client import MealieClient


@dataclass()
class Token(JsonModel):
    _client: "MealieClient" = field(repr=False)
    name: str
    id: int
    token: t.Union[str, None] = None

    def json(self) -> dict:
        return super().json({"name", "id"})

    async def delete(self) -> None:
        await self._client.delete_api_key(self.id)


@dataclass()
class Auth:
    _client: "MealieClient" = field(repr=False)
    access_token: str
    token_type: str = None

    async def refresh(self):
        resp = await self._client.request("auth/refresh")
        self.access_token = resp["access_token"]
        self.token_type = resp["token_type"]

    @property
    def header(self):
        return {aiohttp.hdrs.AUTHORIZATION: f"Bearer {self.access_token}"}
