class MealieError(Exception):
    pass


class UnauthenticatedError(MealieError):
    pass


class BadRequestError(MealieError):
    pass
