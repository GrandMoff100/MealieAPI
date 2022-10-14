import logging
import typing as t

from pydantic import BaseModel as BM
from pydantic.error_wrappers import ValidationError

_LOGGER = logging.getLogger(__name__)

if t.TYPE_CHECKING:
    from mealieapi.client import MealieClient


class BaseModel(BM):
    pass


class InteractiveModel(BaseModel):
    def __init__(self, *args, _client: "MealieClient", **kwargs):
        object.__setattr__(self, "_client", _client)
        try:
            super().__init__(*args, **kwargs)
        except ValidationError as err:
            _LOGGER.debug("%r %r", args, kwargs)
            raise err
