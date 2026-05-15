from datetime import date

from app.models.booking import Booking
from app.repositories.room_repo import RoomRepository
from app.repositories.booking_repo import BookingRepository
from app.utils.exceptions.room import (
    RoomNotFound,
    RoomAlreadyBooked,
    RoomIsNotAvailable,
)
from app.utils.exceptions.booking import (
    BookingNotFound,
    BookingAlreadyCancelled,
    InvalidDateRange,
    ForbiddenBookingAccess
)


class BookingService:
    def __init__(self, booking_repo: BookingRepository, room_repo: RoomRepository):
        self.booking_repo = booking_repo
        self.room_repo = room_repo

    async def create_booking(self, user_id: int, hotel_id: int, room_number: str, check_in: date, check_out: date):
        room = await self.room_repo.find_by_hotel_and_number(hotel_id, room_number)
        if not room:
            raise RoomNotFound()
        if not room.is_available:
            raise RoomIsNotAvailable()

        booked_count = await self.booking_repo.get_booked_count(room.id, check_in, check_out)
        if booked_count >= 1:
            raise RoomAlreadyBooked()

        booking = Booking(
            user_id=user_id,
            room_id=room.id,
            check_in=check_in,
            check_out=check_out,
            total_cost=0,
            status="confirmed"
        )

        try:
            total_cost = booking.calculate_total_cost(room.price_per_night)
        except ValueError as exc:
            raise InvalidDateRange(str(exc))

        booking_data = {
            "user_id": booking.user_id,
            "room_id": booking.room_id,
            "check_in": booking.check_in,
            "check_out": booking.check_out,
            "total_cost": total_cost,
            "status": booking.status
        }
        return await self.booking_repo.add_one(booking_data)

    async def get_user_bookings(self, user_id: int):
        return await self.booking_repo.find_all(user_id=user_id)

    async def cancel_booking(self, booking_id: int, user_id: int):
        booking = await self.booking_repo.find_by_id(booking_id)

        if not booking:
            raise BookingNotFound()

        if booking.user_id != user_id:
            raise ForbiddenBookingAccess("Ви не можете скасувати чуже бронювання")

        try:
            booking.cancel()
        except ValueError:
            raise BookingAlreadyCancelled()

        return await self.booking_repo.update_one(
            booking_id,
            {"status": booking.status}
        )