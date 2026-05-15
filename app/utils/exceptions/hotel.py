from .base import AppError

class HotelNotFound(AppError):
    status_code = 404
    detail = "Hotel not found"