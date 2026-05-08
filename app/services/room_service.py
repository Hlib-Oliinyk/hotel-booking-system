from app.exceptions_handler import RoomNotFound
from app.schemas.room import RoomCreate, RoomUpdate
from app.utils.exceptions.hotel import HotelNotFound
from app.repositories.room_repo import RoomRepository
from app.repositories.hotel_repo import HotelRepository


class RoomService:
    def __init__(self, room_repo: RoomRepository, hotel_repo: HotelRepository):
        self.room_repo = room_repo
        self.hotel_repo = hotel_repo
        
    async def _get_room_or_404(self, room_id: int):
        room = await self.room_repo.find_by_id(room_id)
        if not room:
            raise RoomNotFound()
        return room

    async def create_new_room(self, room_data: RoomCreate):
        hotel = await self.hotel_repo.find_by_id(room_data.hotel_id)
        if not hotel:
            raise HotelNotFound()
        return await self.room_repo.add_one(room_data.model_dump())

    async def get_all_rooms(self, **filters):
        return await self.room_repo.find_all(**filters)

    async def get_room_by_id(self, room_id: int):
        return await self._get_room_or_404(room_id)

    async def update_room(self, room_id: int, room_data: RoomUpdate):
        room = await self._get_room_or_404(room_id) 
        return await self.room_repo.update_one(room.id, room_data.model_dump(exclude_unset=True))

    async def delete_room(self, room_id: int):
        room = await self._get_room_or_404(room_id)

        await self.room_repo.delete_one(row_id=room_id)
        return {
            "message": f"Room {room_id} deleted successfully"
        }