import typing as t
from dataclasses import dataclass, field
from datetime import datetime

from mealieapi.const import YEAR_MONTH_DAY
from mealieapi.misc import name_to_slug
from mealieapi.mixins import JsonModel

if t.TYPE_CHECKING:
    from mealieapi.client import MealieClient


@dataclass()
class Meal(JsonModel):
    _client: "MealieClient" = field(repr=False)
    name: str
    description: str

    @property
    def slug(self):
        return name_to_slug(self.name)

    def json(self) -> t.Dict[str, t.Any]:  # type: ignore[override]
        return super().json({"name", "slug", "description"})

    async def get_recipe(self):
        pass


@dataclass()
class MealPlanDay(JsonModel):
    _client: "MealieClient" = field(repr=False)
    date: datetime
    meals: t.List[Meal]

    def json(self) -> t.Dict[str, t.Any]:  # type: ignore[override]
        data = super().json({"date", "meals"})
        data["date"] = data["date"].strftime(YEAR_MONTH_DAY)
        return data


@dataclass()
class MealPlan(JsonModel):
    _client: "MealieClient" = field(repr=False)
    group: str
    end_date: datetime
    start_date: datetime
    meals: t.List[Meal]
    id: t.Union[int, None] = None
    shopping_list: t.Union[int, None] = None

    def json(self) -> t.Dict[str, t.Any]:  # type: ignore[override]
        data = super().json({"group", "end_date", "start_date", "meals"})
        data["end_date"] = data["end_date"].strftime(YEAR_MONTH_DAY)
        data["start_date"] = data["start_date"].strftime(YEAR_MONTH_DAY)
        return data


@dataclass()
class Ingredient(JsonModel):
    _client: "MealieClient" = field(repr=False)
    title: str
    text: str
    quantity: int
    checked: bool

    def json(self) -> t.Dict[str, t.Any]:  # type: ignore[override]
        return super().json({"title", "text", "quantity", "checked"})


@dataclass()
class ShoppingList(JsonModel):
    _client: "MealieClient" = field(repr=False)
    name: str
    group: str
    items: t.List[Ingredient]
    id: t.Union[int, None] = None

    def json(self) -> t.Dict[str, t.Any]:  # type: ignore[override]
        return super().json({"name", "groups", "items"})

    async def toggle_checked(self, index: int) -> "ShoppingList":
        self.items[index].checked = not self.items[index].checked
        return await self.update()

    def length(self):
        return len(self.items)

    async def create(self) -> "ShoppingList":
        return await self._client.create_shopping_list(self)

    async def update(self) -> "ShoppingList":
        if self.id is not None:
            return await self._client.update_shopping_list(self.id, self)
        else:
            raise ValueError("Missing required attribute id")

    async def delete(self) -> None:
        if self.id is not None:
            await self._client.delete_shopping_list(self.id)
        else:
            raise ValueError("Missing required attribute id")
