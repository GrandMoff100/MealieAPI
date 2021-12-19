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
    id: t.Union[int, None] = None
    categories: t.Union[t.List[RecipeCategory], None] = None
    webhook_urls: t.Union[t.List[str], None] = None
    webhook_time: t.Union[timedelta, None] = None
    users: t.Union[t.List[User], None] = None
    mealplans: t.Union[t.List[MealPlan], None] = None
    shoppinglists: t.Union[t.List[ShoppingList], None] = None
    webhook_enable: t.Union[bool, None] = None

    def json(self) -> dict:
        return super().json({
            'name',
            'webhook_urls',
            'webhook_enable'
        })
