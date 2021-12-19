import typing as t
from dataclasses import dataclass

from mealieapi.auth import Token


@dataclass()
class UserSignup:
    pass


@dataclass()
class User:
    _client: "MealieClient"
    username: str = None
    full_name: str = None
    email: str = None
    admin: bool = False
    group: str = None
    favorite_recipes: list = None
    id: int = None
    tokens: t.List[Token] = None


@dataclass()
class Group:
    name: str = None
