from .base import MealieModel


__all__ = ("AppInfo",)


class AppInfo(MealieModel):
    production: bool
    version: str
    demoStatus: bool
    allowSignup: bool
