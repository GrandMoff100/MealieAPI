from __future__ import annotations

import typing as t

import aiohttp

from mealieapi.model import InteractiveModel


class Token(InteractiveModel):
    name: str
    id: int
    token: str | None = None

    def dict(self, *args, **kwargs) -> dict[str, t.Any]:  # type: ignore[override]
        data = super().dict(*args, **kwargs)
        data.pop("token")
        return data

    async def delete(self) -> None:
        await self._client.delete_api_key(self.id)


class Auth(InteractiveModel):
    access_token: str
    token_type: str | None = None

    async def refresh(self):
        resp = await self._client.request("auth/refresh")
        self.access_token = resp["access_token"]
        self.token_type = resp["token_type"]

    @property
    def header(self):
        return {aiohttp.hdrs.AUTHORIZATION: f"Bearer {self.access_token}"}
