from .base import AppError


class BookingNotFound(AppError):
    pass


class BookingAlreadyCancelled(AppError):
    pass 


class InvalidDateRange(Exception):
    pass

class ForbiddenBookingAccess(Exception):
    pass