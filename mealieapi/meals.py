import typing as t
from dataclasses import dataclass, field
from datetime import datetime

from mealieapi.const import YEAR_MONTH_DAY, YEAR_MONTH_DAY_HOUR_MINUTE_SECOND
from mealieapi.mixins import JsonModel
from mealieapi.misc import name_to_slug


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

    def json(self) -> dict:
        return super().json({
            'name',
            'slug',
            'description'
        })

    async def get_recipe(self):
        pass


@dataclass()
class MealPlanDay(JsonModel):
    _client: "MealieClient" = field(repr=False)
    date: datetime
    meals: t.List[Meal]

    def json(self) -> dict:
        data = super().json({
            'date',
            'meals'
        })
        date['date'] = data['date'].strftime(YEAR_MONTH_DAY)
        return data


@dataclass()
class MealPlan(JsonModel):
    _client: "MealieClient" = field(repr=False)
    group: str
    end_date: datetime
    start_date: datetime
    meals: t.List[Meal]
    uid: t.Union[int, None] = None
    shopping_list: t.Union[int, None] = None

    def json(self) -> dict:
        data = super().json({"group", "end_date", "start_date", "meals"})
        data["end_date"] = data["end_date"].strftime(YEAR_MONTH_DAY)
        data["start_date"] = data["start_date"].strftime(YEAR_MONTH_DAY)
        return data


@dataclass()
class Ingredient(JsonModel):
    _client: "MealieClient" = field(repr=False)


@dataclass()
class ShoppingList(JsonModel):
    _client: "MealieClient" = field(repr=False)
    name: str
    group: str
    items: t.List[Ingredient]
    id: int
