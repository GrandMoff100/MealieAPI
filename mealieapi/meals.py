from __future__ import annotations

import typing as t
from datetime import datetime

import slugify

from mealieapi.const import YEAR_MONTH_DAY
from mealieapi.model import InteractiveModel


class Meal(InteractiveModel):
    name: str
    description: str

    @property
    def slug(self) -> str:
        return slugify.slugify(self.name)

    def dict(self, *args, **kwargs) -> dict[str, t.Any]:
        data = super().dict(*args, **kwargs)
        data.update(slug=self.slug)
        return data

    async def get_recipe(self):
        pass


class MealPlanDay(InteractiveModel):
    date: datetime
    meals: list[Meal]

    def dict(self, *args, **kwargs) -> dict[str, t.Any]:  # type: ignore[override]
        data = super().dict(*args, **kwargs)
        data["date"] = data["date"].strftime(YEAR_MONTH_DAY)
        return data


class MealPlan(InteractiveModel):
    group: str
    end_date: datetime
    start_date: datetime
    meals: list[Meal]
    id: int | None = None
    shopping_list: int | None = None

    def dict(self, *args, **kwargs) -> dict[str, t.Any]:  # type: ignore[override]
        data = super().dict(*args, **kwargs)
        data.pop("id")
        data.pop("shopping_list")
        data["end_date"] = data["end_date"].strftime(YEAR_MONTH_DAY)
        data["start_date"] = data["start_date"].strftime(YEAR_MONTH_DAY)
        return data


class Ingredient(InteractiveModel):
    title: str
    text: str
    quantity: int
    checked: bool


class ShoppingList(InteractiveModel):
    name: str
    group: str
    items: list[Ingredient]
    id: int | None = None

    def dict(self, *args, **kwargs) -> dict[str, t.Any]:  # type: ignore[override]
        data = super().dict(*args, **kwargs)
        data.pop("id")
        return data

    async def toggle_checked(self, index: int) -> "ShoppingList":
        self.items[index].checked = not self.items[index].checked
        return await self.update()

    def length(self) -> int:
        return len(self.items)

    async def create(self) -> "ShoppingList":
        return await self._client.create_shopping_list(self)

    async def update(self) -> "ShoppingList":
        if self.id is not None:
            return await self._client.update_shopping_list(self.id, self)
        raise ValueError("Missing required attribute id")

    async def delete(self) -> None:
        if self.id is not None:
            await self._client.delete_shopping_list(self.id)
        else:
            raise ValueError("Missing required attribute id")
