from fastapi.responses import JSONResponse

from app.utils.exceptions.hotel import HotelNotFound
from app.utils.exceptions.token import InvalidCredentials
from app.utils.exceptions.user import UserExists, UserNotFound, UserForbidden
from app.utils.exceptions.booking import (
    BookingNotFound,
    BookingAlreadyCancelled,
    InvalidDateRange,
    ForbiddenBookingAccess,
)
from app.utils.exceptions.room import RoomNotFound, RoomAlreadyBooked, RoomIsNotAvailable


def _json_error(*, status_code: int, message: str, headers: dict | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": message},
        headers=headers,
    )


def setup_exception_handler(app):
    fixed_handlers: dict[type[Exception], tuple[int, str]] = {
        UserNotFound: (404, "User not found"),
        UserExists: (400, "User already exists"),
        UserForbidden: (403, "Insufficient access rights"),
        HotelNotFound: (404, "Hotel not found"),
        RoomNotFound: (404, "Room not found"),
        RoomAlreadyBooked: (409, "Room already booked"),
        RoomIsNotAvailable: (400, "Room is not available"),
        BookingNotFound: (404, "Booking not found"),
        BookingAlreadyCancelled: (400, "Booking already cancelled"),
    }

    for exc_type, (status_code, message) in fixed_handlers.items():

        @app.exception_handler(exc_type)
        async def _fixed_handler(request, exc, _status_code=status_code, _message=message):
            return _json_error(status_code=_status_code, message=_message)

    @app.exception_handler(InvalidCredentials)
    async def invalid_credentials_handler(request, exc):
        return _json_error(
            status_code=401,
            message="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(InvalidDateRange)
    async def invalid_date_range_handler(request, exc):
        # Використовуємо str(exc), щоб передати текст "Дата заїзду має бути раніше..."
        # або дефолтний текст, якщо помилка викликана без аргументів
        error_msg = str(exc) if str(exc) else "Invalid date range"
        return _json_error(status_code=400, message=error_msg)

    @app.exception_handler(ForbiddenBookingAccess)
    async def forbidden_booking_access_handler(request, exc):
        error_msg = (
            str(exc) if str(exc) else "Insufficient access rights for this booking"
        )
        return _json_error(status_code=403, message=error_msg)
