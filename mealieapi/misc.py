import re
import typing as t
from slugify import slugify
from dataclasses import dataclass, field

if t.TYPE_CHECKING:
    from mealieapi.client import MealieClient


def name_to_slug(name: str) -> str:
    return slugify(name)


def camel_to_snake_case(obj):
    if isinstance(obj, dict):
        for key, value in list(obj.items()):
            new_key = camel_to_snake_case(key)
            del obj[key]
            obj[new_key] = value
            if isinstance(value, dict) or isinstance(value, list):
                obj[new_key] = camel_to_snake_case(value)
        return obj
    elif isinstance(obj, list):
        return [camel_to_snake_case(item) for item in obj]
    elif isinstance(obj, str):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", obj).lower()


@dataclass()
class File:
    _client: "MealieClient" = field(repr=False, compare=False)
    file_token: str

    async def download(self) -> bytes:
        return await self._client.download_file(self.file_token)


@dataclass()
class DebugInfo:
    production: t.Optional[bool] = None
    version: t.Optional[str] = None
    demo_status: t.Optional[bool] = None
    api_port: t.Optional[int] = None
    api_docs: t.Optional[bool] = None
    db_type: t.Optional[str] = None
    db_url: t.Optional[str] = None
    default_group: t.Optional[str] = None


@dataclass()
class DebugStatistics:
    total_recipes: t.Optional[int] = None
    total_users: t.Optional[int] = None
    total_groups: t.Optional[int] = None
    uncategorized_recipes: t.Optional[int] = None
    untagged_recipes: t.Optional[int] = None


@dataclass()
class DebugVersion:
    production: t.Optional[bool] = None
    version: t.Optional[str] = None
    demo_status: t.Optional[bool] = None
