from .base import AppError


class RoomNotFound(AppError):
    pass


class RoomAlreadyBooked(AppError):
    pass


class RoomIsNotAvailable(AppError):
    pass