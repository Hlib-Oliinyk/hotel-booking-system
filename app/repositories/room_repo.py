from sqlalchemy import select

from app.models.room import Room
from app.repositories.base import BaseRepository


class RoomRepository(BaseRepository):
    model = Room

    async def get_available_rooms(self):
        return await self.find_all(is_available=True)

    async def find_by_hotel_and_number(self, hotel_id: int, number: str):
        result = await self.db.execute(
            select(Room).where(Room.hotel_id == hotel_id, Room.number == number)
        )
        return result.scalar_one_or_none()