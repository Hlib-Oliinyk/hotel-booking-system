from typing import Coroutine

from app.models.room import Room
from app.repositories.base import BaseRepository


class RoomRepository(BaseRepository):
    model = Room

    async def get_available_rooms(self) -> Coroutine:
        return await self.find_all(is_available=True)