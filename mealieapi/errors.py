class MealieError(Exception):
    pass


class UnauthenticatedError(MealieError):
    pass


class BadRequestError(MealieError):
    pass


class ParameterMissingError(MealieError):
    pass


class InternalServerError(MealieError):
    pass
