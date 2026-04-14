from .base import AppError


class UserExists(AppError):
    pass


class UserNotFound(AppError):
    pass


class UserForbidden(AppError):
    pass