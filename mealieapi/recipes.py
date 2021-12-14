import typing as t

from dataclasses import dataclass
from datetime import datetime


@dataclass()
class Recipe:
    _client: "MealieClient"
    slug: str
    name: str = None
    description: str = None
    image: str = None
    recipe_yield: str = None
    recipe_ingredient: t.List[str] = None
    recipe_instructions: t.List[t.Dict[str, str]] = None
    tags: t.List[str] = None
    recipe_category: t.List[str] = None
    notes: t.List[t.Dict[str, str]] = None
    rating: int = None
    extras: t.Dict[str, str] = None
    id: int = None
    settings: t.Dict[str, bool] = None
    total_time: str = None
    prep_time: str = None
    perform_time: str = None
    nutrition: t.Dict[str, str] = None
    date_added: datetime = None
    date_updated: datetime = None
    org_url: str = None
    tools: list
    assets: list
    comments: str

    def json(self):
        attrs = {
            "slug",
            "name",
            "description",
            "image",
            "recipe_yield",
            "recipe_ingredient",
            "recipe_instructions",
            "tags",
            "recipe_category",
            "notes",
            "org_url",
            "rating",
            "extras",
            'id',
            'settings',
            'total_time',
            'prep_time',
            'perform_time',
            'nutrition',
            'date_added',
            'date_updated',
            'tools',
            'assets',
            'comments'
        }
        return {attr: getattr(self, attr) for attr in attrs}

    async def create(self) -> "Recipe":
        return await self._client.create_recipe(self)

    async def get_image(self, type='original') -> bytes:
        """
        Gets the image for the recipe.
        Valid types are :code:`original`, :code:`min-original`, and :code:`tiny-original`
        """
        if self.image:
            return await self._client.request(f'media/recipes/{self.slug}/images/{type}.webp')

    async def delete(self) -> "Recipe":
        return await self._client.delete_recipe(self.slug)

    async def get_asset(self, file_name: str):
        return await self._client.request(f'media/recipes/{self.slug}/assets/{file_name}')

    async def sync_changes(self) -> "Recipe":
        return await self._client.patch_recipe(self)