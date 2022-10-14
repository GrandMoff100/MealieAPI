import re

from mealieapi.model import BaseModel, InteractiveModel


def camel_to_snake_case(obj):
    if isinstance(obj, dict):
        for key, value in list(obj.items()):
            new_key = camel_to_snake_case(key)
            del obj[key]
            obj[new_key] = value
            if isinstance(value, dict):
                obj[new_key] = camel_to_snake_case(value)
        return obj
    if isinstance(obj, list):
        return [camel_to_snake_case(item) for item in obj]
    if isinstance(obj, str):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", obj).lower()
    raise ValueError(f"Unexpected object {obj!r}")


class File(InteractiveModel):
    file_token: str

    async def download(self) -> bytes:
        return await self._client.download_file(self.file_token)


class AppVersion(BaseModel):
    production: bool | None = None
    version: str | None = None
    demo_status: bool | None = None
    allow_signup: bool | None = None


class DebugInfo(BaseModel):
    production: bool | None = None
    version: str | None = None
    demo_status: bool | None = None
    api_port: int | None = None
    api_docs: bool | None = None
    db_type: str | None = None
    db_url: str | None = None
    default_group: str | None = None


class DebugStatistics(BaseModel):
    total_recipes: int | None = None
    total_users: int | None = None
    total_groups: int | None = None
    uncategorized_recipes: int | None = None
    untagged_recipes: int | None = None


class DebugVersion(BaseModel):
    production: bool | None = None
    version: str | None = None
    demo_status: bool | None = None
