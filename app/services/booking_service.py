from datetime import date
from fastapi import HTTPException

from app.repositories.room_repo import RoomRepository
from app.repositories.booking_repo import BookingRepository
from app.exceptions_handler import (
    RoomNotFound,
    RoomAlreadyBooked,
    RoomIsNotAvailable,
    BookingNotFound,
    BookingAlreadyCancelled
)


class BookingService:
    def __init__(self, booking_repo: BookingRepository, room_repo: RoomRepository):
        self.booking_repo = booking_repo
        self.room_repo = room_repo

    async def create_booking(self, user_id: int, hotel_id: int, room_number: str, check_in: date, check_out: date):
        if check_in >= check_out:
            raise HTTPException(status_code=400, detail="Дата заїзду має бути раніше дати виїзду")

        room = await self.room_repo.find_by_hotel_and_number(hotel_id, room_number)
        if not room:
            raise RoomNotFound()
        if not room.is_available:
            raise RoomIsNotAvailable()

        booked_count = await self.booking_repo.get_booked_count(room.id, check_in, check_out)
        if booked_count >= 1:
            raise RoomAlreadyBooked()

        days = (check_out - check_in).days
        total_cost = days * room.price_per_night

        booking_data = {
            "user_id": user_id,
            "room_id": room.id,
            "check_in": check_in,
            "check_out": check_out,
            "total_cost": total_cost,
            "status": "confirmed"
        }
        return await self.booking_repo.add_one(booking_data)

    async def get_user_bookings(self, user_id: int):
        return await self.booking_repo.find_all(user_id=user_id)

    async def cancel_booking(self, booking_id: int, user_id: int):
        booking = await self.booking_repo.find_by_id(booking_id)

        if not booking:
            raise BookingNotFound()

        if booking.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Ви не можете скасувати чуже бронювання"
            )

        if booking.status == "cancelled":
            raise BookingAlreadyCancelled()

        return await self.booking_repo.update_one(
            booking_id,
            {"status": "cancelled"}
        )