from fastapi.responses import JSONResponse

from app.utils.exceptions.hotel import HotelNotFound
from app.utils.exceptions.token import InvalidCredentials
from app.utils.exceptions.user import UserExists, UserNotFound, UserForbidden
from app.utils.exceptions.booking import BookingNotFound, BookingAlreadyCancelled, InvalidDateRange, ForbiddenBookingAccess
from app.utils.exceptions.room import RoomNotFound, RoomAlreadyBooked, RoomIsNotAvailable


def setup_exception_handler(app):
    @app.exception_handler(UserNotFound)
    async def user_not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"details": "User not found"}
        )

    @app.exception_handler(UserExists)
    async def user_exists_handler(request, exc):
        return JSONResponse(
            status_code=400,
            content={"details": "User already exists"}
        )

    @app.exception_handler(UserForbidden)
    async def user_forbidden_handler(request, exc):
        return JSONResponse(
            status_code=403,
            content={"details": "Insufficient access rights"}
        )

    @app.exception_handler(InvalidCredentials)
    async def invalid_credentials_handler(request, exc):
        return JSONResponse(
            status_code=401,
            content={"detail": "Could not validate credentials"},
            headers={"WWW-Authenticate": "Bearer"}
        )

    @app.exception_handler(HotelNotFound)
    async def hotel_not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"details": "Hotel not found"}
        )

    @app.exception_handler(RoomNotFound)
    async def room_not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"details": "Room not found"}
        )

    @app.exception_handler(RoomAlreadyBooked)
    async def room_already_booked_handler(request, exc):
        return JSONResponse(
            status_code=409,
            content={"details": "Room already booked"}
        )

    @app.exception_handler(RoomIsNotAvailable)
    async def room_is_not_available_handler(request, exc):
        return JSONResponse(
            status_code=400,
            content={"details": "Room is not available"}
        )

    @app.exception_handler(BookingNotFound)
    async def booking_not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"details": "Booking not found"}
        )

    @app.exception_handler(BookingAlreadyCancelled)
    async def booking_already_cancelled_handler(request, exc):
        return JSONResponse(
            status_code=400,
            content={"details": "Booking already cancelled"}
        )
        
    @app.exception_handler(InvalidDateRange)
    async def invalid_date_range_handler(request, exc):
        # Використовуємо str(exc), щоб передати текст "Дата заїзду має бути раніше..." 
        # або дефолтний текст, якщо помилка викликана без аргументів
        error_msg = str(exc) if str(exc) else "Invalid date range"
        return JSONResponse(
            status_code=400,
            content={"details": error_msg}
        )

    @app.exception_handler(ForbiddenBookingAccess)
    async def forbidden_booking_access_handler(request, exc):
        error_msg = str(exc) if str(exc) else "Insufficient access rights for this booking"
        return JSONResponse(
            status_code=403,
            content={"details": error_msg}
        )