from __future__ import annotations

import io
import typing as t
from datetime import timedelta

from mealieapi.auth import Token
from mealieapi.meals import MealPlan, ShoppingList
from mealieapi.model import InteractiveModel
from mealieapi.recipes import Recipe, RecipeCategory


class User(InteractiveModel):
    username: str
    full_name: str
    email: str
    admin: bool
    group: str
    id: str
    favorite_recipes: list[Recipe] | None = None
    tokens: list[Token] | None = None
    password: str | None = None

    def dict(self, *args, **kwargs) -> dict[str, t.Any]:  # type: ignore[override]
        data = super().dict(*args, **kwargs)
        data.pop("tokens")
        data.pop("password")
        return data

    async def create(self) -> "User":
        return await self._client.create_user(self)

    async def update(self) -> "User":
        return await self._client.update_user(self.id, self)

    async def delete(self) -> None:
        await self._client.delete_user(self.id)

    async def reset_password(self) -> None:
        await self._client.reset_password(self.id)

    async def update_password(self, new_password: str):
        if self.password:
            await self._client.update_password(self.id, self.password, new_password)
        else:
            raise ValueError("Missing password attribute, required to change password.")

    async def favorites(self) -> list[Recipe] | None:
        return await self._client.get_favorites(self.id)

    async def add_favorite(self, recipe_slug: str) -> None:
        await self._client.add_favorite(self.id, recipe_slug)

    async def remote_favorite(self, recipe_slug: str) -> None:
        await self._client.remove_favorite(self.id, recipe_slug)

    async def image(self) -> bytes:
        return await self._client.get_user_image(self.id)

    async def update_image(self, image: io.BytesIO) -> bytes:
        return await self._client.update_user_image(self.id, image)


class Group(InteractiveModel):
    name: str
    id: int | None = None
    categories: list[RecipeCategory] | None = None
    webhook_urls: list[str] | None = None
    webhook_time: timedelta | None = None
    users: list[User] | None = None
    mealplans: list[MealPlan] | None = None
    shopping_lists: list[ShoppingList] | None = None
    webhook_enable: bool | None = None

    def dict(self, *args, **kwargs) -> dict[str, t.Any]:  # type: ignore[override]
        data = super().dict(*args, **kwargs)
        data.pop("id")
        data.pop("categories")
        data.pop("users")
        data.pop("mealplans")
        data.pop("shopping_lists")
        return data

    async def create(self) -> "Group":
        return await self._client.create_group(self)

    async def update(self) -> "Group":
        if self.id is not None:
            return await self._client.update_group(self.id, self)
        raise ValueError("Missing required parameter id")

    async def delete(self) -> None:
        if self.id is not None:
            await self._client.delete_group(self.id)
        else:
            raise ValueError("Missing required parameter id")


class UserSignup(InteractiveModel):
    name: str
    admin: bool
    token: str | None = None

    def dict(self, *args, **kwargs) -> dict[str, t.Any]:  # type: ignore[override]
        data = super().dict(*args, **kwargs)
        data.pop("token")
        return data

    async def delete(self) -> None:
        await self._client.delete_signup_token(self.token)

    async def signup(self, user: User) -> User:
        if self.token:
            return await self._client.signup_with_token(self.token, user)
        raise ValueError("Tried to signup user without signup token")
