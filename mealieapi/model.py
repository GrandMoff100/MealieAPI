import typing as t

from pydantic import BaseModel as BM

if t.TYPE_CHECKING:
    from mealieapi.client import MealieClient


class BaseModel(BM):
    pass


class InteractiveModel(BaseModel):
    def __init__(self, *args, _client: "MealieClient", **kwargs):
        object.__setattr__(self, "_client", _client)
        super().__init__(*args, **kwargs)
