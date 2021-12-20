class MealieError(Exception):
    pass


class UnauthenticatedError(MealieError):
    pass


class BadRequestError(MealieError):
    pass


class ParameterMissingError(MealieError):
    pass


class UserError(MealieError):
    pass
