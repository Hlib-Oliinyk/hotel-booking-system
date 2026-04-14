from .base import AppError


class BookingNotFound(AppError):
    pass


class BookingAlreadyCancelled(AppError):
    pass