from dataclasses import dataclass


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
