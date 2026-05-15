from .base import AppError


class BookingNotFound(AppError):
    status_code = 404
    detail = "Booking not found"

class BookingAlreadyCancelled(AppError):
    status_code = 400
    detail = "Booking already cancelled"

class InvalidDateRange(AppError):
    status_code = 400
    detail = "Invalid date range"

class ForbiddenBookingAccess(AppError):
    status_code = 403
    detail = "Insufficient access rights for this booking"
