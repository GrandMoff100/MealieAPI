import typing as t
from dataclasses import dataclass, field

import aiohttp

from mealieapi.mixins import JsonModel

if t.TYPE_CHECKING:
    from mealieapi.client import MealieClient
    from mealieapi.raw import RawClient


@dataclass()
class Token(JsonModel):
    _client: "MealieClient" = field(repr=False)
    name: t.Optional[str] = None
    id: t.Optional[int] = None
    token: t.Optional[str] = None

    def json(self) -> t.Dict[str, t.Any]:  # type: ignore[override]
        return super().json(
            {
                "name",
            }
        )

    async def delete(self) -> None:
        if self.id is not None:
            await self._client.delete_api_key(self.id)
        else:
            raise ValueError('Token.id must not be None')

    def __eq__(self, other) -> bool:
        if isinstance(other, Token):
            checks = ["name", "id", "token"]
            for check in checks:
                if getattr(self, check) != getattr(other, check):
                    return False
            return True
        return False


@dataclass()
class Auth:
    _client: "RawClient" = field(repr=False, compare=False)
    access_token: str
    token_type: t.Optional[str] = None

    async def refresh(self):
        resp = await self._client.request("auth/refresh")
        self.access_token = resp["access_token"]
        self.token_type = resp["token_type"]

    @property
    def header(self):
        return {aiohttp.hdrs.AUTHORIZATION: f"Bearer {self.access_token}"}
