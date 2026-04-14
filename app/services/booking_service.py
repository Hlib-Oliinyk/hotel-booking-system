from datetime import date
from fastapi import HTTPException

from app.repositories.room_repo import RoomRepository
from app.repositories.booking_repo import BookingRepository
from app.exceptions_handler import RoomNotFound, RoomAlreadyBooked


class BookingService:
    def __init__(self, booking_repo: BookingRepository, room_repo: RoomRepository):
        self.booking_repo = booking_repo
        self.room_repo = room_repo

    async def create_booking(self, user_id: int, room_id: int, check_in: date, check_out: date):
        if check_in >= check_out:
            raise HTTPException(
                status_code=400,
                detail="Дата заїзду має бути раніше дати виїзду"
            )

        room = await self.room_repo.find_by_id(room_id)
        if not room:
            raise RoomNotFound()

        booked_count = await self.booking_repo.get_booked_count(room_id, check_in, check_out)
        if booked_count >= 1:
            raise RoomAlreadyBooked()

        days = (check_out - check_in).days
        total_cost = days * room.price_per_night

        booking_data = {
            "user_id": user_id,
            "room_id": room_id,
            "check_in": check_in,
            "check_out": check_out,
            "total_cost": total_cost,
            "status": "confirmed"
        }
        return await self.booking_repo.add_one(booking_data)