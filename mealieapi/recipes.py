import typing as t
from datetime import date, datetime
from zipfile import ZipFile

import slugify

from mealieapi.const import YEAR_MONTH_DAY, YEAR_MONTH_DAY_HOUR_MINUTE_SECOND
from mealieapi.model import BaseModel, InteractiveModel

if t.TYPE_CHECKING:
    from mealieapi.users import User


class RecipeImage(InteractiveModel):
    recipe_slug: str
    image: int


class RecipeAsset(InteractiveModel):
    recipe_slug: str
    file_name: str
    name: str | None = None
    icon: str | None = None

    async def content(self) -> bytes:
        return await self._client.get_asset(self.recipe_slug, self.file_name)


class RecipeNutrition(BaseModel):
    calories: float | None = None
    fatContent: float | None = None
    proteinContent: float | None = None
    carbohydrateContent: float | None = None
    fiberContent: float | None = None
    sodiumContent: float | None = None
    sugarContent: float | None = None


class RecipeComment(InteractiveModel):
    recipe_slug: str
    text: str
    id: int
    uuid: str
    date_added: date
    user: "User"

    def dict(self, *args, **kwargs) -> dict[str, t.Any]:  # type: ignore[override]
        return {"text": self.text}

    async def create(self) -> "RecipeComment":
        return await self._client.create_recipe_comment(self.recipe_slug, self)

    async def update(self, text: str) -> "RecipeComment":
        new_comment = self.copy()
        new_comment.text = text
        return await self._client.update_recipe_comment(
            self.recipe_slug, self.id, new_comment
        )

    async def delete(self) -> None:
        await self._client.delete_recipe_comment(self.recipe_slug, self.id)


class Recipe(InteractiveModel):
    name: str
    description: str | None = None
    image: str | None = None
    recipe_yield: str | None = None
    recipe_ingredient: list[str] | None = None
    recipe_instructions: list[dict[str, str]] | None = None
    tags: list[str] | None = None
    recipe_category: list[str] | None = None
    notes: list[dict[str, str]] | None = None
    rating: int | None = None
    extras: dict[str, str] | None = None
    id: int | None = None
    settings: dict[str, bool] | None = None
    total_time: str | None = None
    prep_time: str | None = None
    perform_time: str | None = None
    nutrition: RecipeNutrition | None = None
    date_added: date | None = None
    date_updated: datetime | None = None
    org_url: str | None = None
    tools: list | None = None
    assets: list[RecipeAsset] | None = None
    comments: list[RecipeComment] | None = None

    @property
    def slug(self) -> str:
        return slugify.slugify(self.name)

    def dict(self, *args, **kwargs) -> dict[str, t.Any]:  # type: ignore[override]
        data = super().dict(*args, **kwargs)
        data.update(slug=self.slug)
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

    async def get_image(self, _type="original") -> bytes | None:
        """
        Gets the image for the recipe.
        Valid types are :code:`original`, :code:`min-original`, and :code:`tiny-original`
        """
        if self.image is not None:
            return await self._client.get_image(self.slug, _type)
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


class RecipeTag(InteractiveModel):
    id: int
    name: str
    recipes: list[Recipe] | None = None

    @property
    def slug(self) -> str:
        return slugify.slugify(self.name)

    def dict(self, *args, **kwargs) -> dict[str, t.Any]:  # type: ignore[override]
        data = super().dict(*args, **kwargs)
        data.pop("id")
        return data

    async def update(self, new_name: str) -> "RecipeTag":
        return await self._client.update_tag(self.slug, new_name)

    async def delete(self):
        await self._client.delete_tag(self.id)


class RecipeCategory(InteractiveModel):
    id: int
    name: str
    recipes: list[Recipe] | None = None

    @property
    def slug(self):
        return slugify.slugify(self.name)

    def dict(self, *args, **kwargs) -> dict[str, t.Any]:  # type: ignore[override]
        data = super().dict(*args, **kwargs)
        data.pop("id")
        return data
