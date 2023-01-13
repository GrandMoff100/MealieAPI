from pydantic import BaseModel


class MealieModel(BaseModel):
    class Config:
        orm_mode = True
