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
class UserSignup(JsonModel):
    _client: "MealieClient" = field(repr=False)
    name: str
    admin: bool
    token: t.Union[str, None] = None

    def json(self) -> dict:
        return super().json({"name", "admin"})


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

    def json(self) -> dict:
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

    async def create_with_token(self):
        pass


@dataclass()
class Group(JsonModel):
    _client: "MealieClient" = field(repr=False)
    name: str
    id: int
    categories: t.List[RecipeCategory]
    webhook_urls: t.List[str]
    webhook_time: timedelta
    webhook_enable: bool
    users: t.List[User]
    mealplans: t.List[MealPlan]
    shoppinglists: t.List[ShoppingList]
