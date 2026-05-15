from .base import AppError


class InvalidCredentials(AppError):
    status_code = 401
    detail = "Could not validate credentials"
    headers = {"WWW-Authenticate": "Bearer"}
