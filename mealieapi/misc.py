import re
import typing as t
from dataclasses import dataclass

JSONObject = t.Union[list, t.Union[dict, str]]
if t.TYPE_CHECKING:
    from mealieapi.client import MealieClient


def name_to_slug(name):
    letters = filter(lambda char: char in "qwertyuiopasdfghjklzxcvbnm ", name.lower())
    return "".join(letters).replace(" ", "-")


def camel_to_snake_case(obj: JSONObject):
    if isinstance(obj, dict):
        for key, value in list(obj.items()):
            new_key = camel_to_snake_case(key)
            del obj[key]
            obj[new_key] = value
            if isinstance(value, dict):
                obj[new_key] = camel_to_snake_case(value)
        return obj
    elif isinstance(obj, list):
        return [camel_to_snake_case(item) for item in obj]
    elif isinstance(obj, str):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", obj).lower()


@dataclass()
class File:
    _client: "MealieClient"
    file_token: str

    async def download(self):
        pass


@dataclass()
class DebugInfo:
    production: bool = None
    version: str = None
    demo_status: bool = None
    api_port: int = None
    api_docs: bool = None
    db_type: str = None
    db_url: str = None
    default_group: str = None


@dataclass()
class DebugStatistics:
    total_recipes: int = None
    total_users: int = None
    total_groups: int = None
    uncategorized_recipes: int = None
    untagged_recipes: int = None


@dataclass()
class DebugVersion:
    production: bool = None
    version: str = None
    demo_status: bool = None
