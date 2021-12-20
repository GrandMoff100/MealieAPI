import typing as t
from dataclasses import dataclass, field
from datetime import datetime
from zipfile import ZipFile

from mealieapi.const import YEAR_MONTH_DAY, YEAR_MONTH_DAY_HOUR_MINUTE_SECOND
from mealieapi.misc import name_to_slug
from mealieapi.mixins import JsonModel

if t.TYPE_CHECKING:
    from mealieapi.client import MealieClient
    from mealieapi.users import User


@dataclass()
class RecipeImage(JsonModel):
    _client: "MealieClient" = field(repr=False)
    recipe_slug: str
    image: int


@dataclass()
class RecipeAsset(JsonModel):
    _client: "MealieClient" = field(repr=False)
    recipe_slug: str
    file_name: str
    name: t.Optional[str] = None
    icon: t.Optional[str] = None

    async def content(self) -> bytes:
        return await self._client.get_asset(self.recipe_slug, self.file_name)


@dataclass()
class RecipeNutrition:
    calories: t.Optional[float] = None
    fatContent: t.Optional[float] = None
    proteinContent: t.Optional[float] = None
    carbohydrateContent: t.Optional[float] = None
    fiberContent: t.Optional[float] = None
    sodiumContent: t.Optional[float] = None
    sugarContent: t.Optional[float] = None


@dataclass()
class RecipeComment(JsonModel):
    _client: "MealieClient" = field(repr=False)
    recipe_slug: str
    text: str
    id: int
    uuid: str
    date_added: datetime
    user: "User"

    def json(self) -> t.Dict[str, t.Any]:  # type: ignore[override]
        return super().json(
            {
                "text",
            }
        )

    async def create(self) -> "RecipeComment":
        return await self._client.create_recipe_comment(self.recipe_slug, self)

    async def update(self, text: str) -> "RecipeComment":
        return await self._client.update_recipe_comment(self.recipe_slug, self.id, self)

    async def delete(self) -> None:
        await self._client.delete_recipe_comment(self.recipe_slug, self.id)


@dataclass(repr=False)
class Recipe(JsonModel):
    _client: "MealieClient" = field(repr=False)
    name: str
    description: t.Optional[str] = None
    image: t.Optional[str] = None
    recipe_yield: t.Optional[str] = None
    recipe_ingredient: t.Optional[t.List[str]] = None
    recipe_instructions: t.Optional[t.List[t.Dict[str, str]]] = None
    tags: t.Optional[t.List[str]] = None
    recipe_category: t.Optional[t.List[str]] = None
    notes: t.Optional[t.List[t.Dict[str, str]]] = None
    rating: t.Optional[int] = None
    extras: t.Optional[t.Dict[str, str]] = None
    id: t.Optional[int] = None
    settings: t.Optional[t.Dict[str, bool]] = None
    total_time: t.Optional[str] = None
    prep_time: t.Optional[str] = None
    perform_time: t.Optional[str] = None
    nutrition: t.Optional[RecipeNutrition] = None
    date_added: t.Optional[datetime] = None
    date_updated: t.Optional[datetime] = None
    org_url: t.Optional[str] = None
    tools: t.Optional[list] = None
    assets: t.Optional[t.List[RecipeAsset]] = None
    comments: t.Optional[t.List[RecipeComment]] = None

    @property
    def slug(self):
        return name_to_slug(self.name)

    def json(self) -> t.Dict[str, t.Any]:  # type: ignore[override]
        data = super().json(
            {
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
                "id",
                "settings",
                "total_time",
                "prep_time",
                "perform_time",
                "nutrition",
                "date_added",
                "date_updated",
                "tools",
                "assets",
                "comments",
            }
        )
        if data["date_added"]:
            data["date_added"] = data["date_added"].strftime(YEAR_MONTH_DAY)
        if data["date_updated"]:
            data["date_updated"] = data["date_updated"].strftime(
                YEAR_MONTH_DAY_HOUR_MINUTE_SECOND
            )
        return data

    async def create(self) -> "Recipe":
        return await self._client.create_recipe(self)

    async def delete(self) -> "Recipe":
        return await self._client.delete_recipe(self.slug)

    async def get_asset(self, file_name: str):
        return await self._client.get_asset(self.slug, file_name)

    async def get_image(self, type="original") -> t.Optional[bytes]:
        """
        Gets the image for the recipe.
        Valid types are :code:`original`, :code:`min-original`, and :code:`tiny-original`
        """
        if self.image is not None:
            return await self._client.get_image(self.slug, type)
        return None

    async def push_changes(self) -> "Recipe":
        return await self._client.update_recipe(self)

    async def get_zip(self) -> ZipFile:
        return await self._client.get_recipe_zip(self.slug)

    async def refresh(self) -> None:
        recipe = await self._client.get_recipe(self.slug)
        for attr in dir(recipe):
            if not attr.startswith("_"):
                setattr(self, attr, getattr(recipe, attr))

    def __repr__(self):
        return f"<Recipe {self.slug!r}>"


@dataclass()
class RecipeTag(JsonModel):
    _client: "MealieClient" = field(repr=False)
    id: int
    name: str
    recipes: t.Optional[t.List[Recipe]] = None

    @property
    def slug(self) -> str:
        return name_to_slug(self.name)

    def json(self) -> t.Dict[str, t.Any]:  # type: ignore[override]
        return super().json({"name", "slug"})

    async def update(self, new_name: str) -> "RecipeTag":
        return await self._client.update_tag(self.slug, new_name)

    async def delete(self):
        await self._client.delete_tag(self.id)


@dataclass()
class RecipeCategory(JsonModel):
    _client: "MealieClient" = field(repr=False)
    id: int
    name: str
    recipes: t.Optional[t.List[Recipe]] = None

    @property
    def slug(self):
        return name_to_slug(self.name)

    def json(self) -> t.Dict[str, t.Any]:  # type: ignore[override]
        return super().json({"name", "slug"})
