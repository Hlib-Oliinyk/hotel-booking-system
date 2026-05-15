from .base import AppError


class RoomNotFound(AppError):
    status_code = 404
    detail = "Room not found"

class RoomAlreadyBooked(AppError):
    status_code = 409
    detail = "Room already booked"

class RoomIsNotAvailable(AppError):
    status_code = 400
    detail = "Room is not available"