import io
import typing as t
from dataclasses import dataclass, field
from datetime import timedelta

from mealieapi.auth import Token
from mealieapi.meals import MealPlan, ShoppingList
from mealieapi.mixins import JsonModel
from mealieapi.recipes import Recipe, RecipeCategory

if t.TYPE_CHECKING:
    from mealieapi.client import MealieClient


@dataclass()
class User(JsonModel):
    _client: "MealieClient" = field(repr=False)
    username: str
    full_name: str
    email: str
    admin: bool
    group: str
    id: int
    favorite_recipes: t.Union[t.List[Recipe], None] = None
    tokens: t.Union[t.List[Token], None] = None
    password: t.Union[str, None] = None

    def json(self) -> t.Dict[str, t.Any]:  # type: ignore[override]
        return super().json(
            {
                "username",
                "full_name",
                "email",
                "admin",
                "group",
                "password",
                "id",
                "favorite_recipes",
            }
        )

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

    async def favorites(self) -> t.Optional[t.List[Recipe]]:
        return await self._client.get_favorites(self.id)

    async def add_favorite(self, recipe_slug: str) -> None:
        await self._client.add_favorite(self.id, recipe_slug)

    async def remote_favorite(self, recipe_slug: str) -> None:
        await self._client.remove_favorite(self.id, recipe_slug)

    async def image(self) -> bytes:
        return await self._client.get_user_image(self.id)

    async def update_image(self, image: io.BytesIO) -> bytes:
        return await self._client.update_user_image(self.id, image)


@dataclass()
class Group(JsonModel):
    _client: "MealieClient" = field(repr=False)
    name: str
    id: t.Union[int, None] = None
    categories: t.Union[t.List[RecipeCategory], None] = None
    webhook_urls: t.Union[t.List[str], None] = None
    webhook_time: t.Union[timedelta, None] = None
    users: t.Union[t.List[User], None] = None
    mealplans: t.Union[t.List[MealPlan], None] = None
    shopping_lists: t.Union[t.List[ShoppingList], None] = None
    webhook_enable: t.Union[bool, None] = None

    def json(self) -> t.Dict[str, t.Any]:  # type: ignore[override]
        return super().json({"name", "webhook_urls", "webhook_enable"})

    async def create(self) -> "Group":
        return await self._client.create_group(self)

    async def update(self) -> "Group":
        if self.id is not None:
            return await self._client.update_group(self.id, self)
        else:
            raise ValueError("Missing required parameter id")

    async def delete(self) -> None:
        if self.id is not None:
            await self._client.delete_group(self.id)
        else:
            raise ValueError("Missing required parameter id")


@dataclass()
class UserSignup(JsonModel):
    _client: "MealieClient" = field(repr=False)
    name: str
    admin: bool
    token: t.Union[str, None] = None

    def json(self) -> t.Dict[str, t.Any]:  # type: ignore[override]
        return super().json({"name", "admin"})

    async def delete(self) -> None:
        await self._client.delete_signup_token(self.token)

    async def signup(self, user: User) -> User:
        if self.token:
            return await self._client.signup_with_token(self.token, user)
        else:
            raise ValueError("Tried to signup user without signup token")
