from .base import AppError


class UserExists(AppError):
    status_code = 400
    detail = "User already exists"

class UserNotFound(AppError):
    status_code = 404
    detail = "User not found"

class UserForbidden(AppError):
    status_code = 403
    detail = "Insufficient access rights"
