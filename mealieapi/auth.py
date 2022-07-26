import typing as t

import aiohttp

from mealieapi.model import InteractiveModel

if t.TYPE_CHECKING:
    from mealieapi.client import MealieClient
    from mealieapi.raw import RawClient


class Token(InteractiveModel):
    name: str
    id: int
    token: t.Union[str, None] = None

    def json(self) -> t.Dict[str, t.Any]:  # type: ignore[override]
        return super().json({"name", "id"})

    async def delete(self) -> None:
        await self._client.delete_api_key(self.id)


class Auth(InteractiveModel):
    access_token: str
    token_type: t.Optional[str] = None

    async def refresh(self):
        resp = await self._client.request("auth/refresh")
        self.access_token = resp["access_token"]
        self.token_type = resp["token_type"]

    @property
    def header(self):
        return {aiohttp.hdrs.AUTHORIZATION: f"Bearer {self.access_token}"}
