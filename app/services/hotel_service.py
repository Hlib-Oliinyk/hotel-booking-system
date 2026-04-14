from app.schemas.hotel import HotelCreate
from app.exceptions_handler import HotelNotFound
from app.repositories.hotel_repo import HotelRepository


class HotelService:
    def __init__(self, hotel_repo: HotelRepository):
        self.hotel_repo = hotel_repo

    async def get_all_hotels(self, location: str | None = None, stars: int | None = None):
        return await self.hotel_repo.get_filtered_hotels(location=location, stars=stars)

    async def add_hotel(self, hotel_data: HotelCreate):
        return await self.hotel_repo.add_one(hotel_data.model_dump())

    async def get_hotel_by_id(self, hotel_id: int):
        return await self.hotel_repo.find_by_id(hotel_id)

    async def update_hotel(self, hotel_id: int, hotel_data: HotelCreate):
        hotel = await self.hotel_repo.find_by_id(hotel_id)
        if not hotel:
            raise HotelNotFound()

        return await self.hotel_repo.update_one(
            hotel_id,
            hotel_data.model_dump()
        )

    async def delete_hotel(self, hotel_id: int):
        hotel = await self.hotel_repo.find_by_id(hotel_id)
        if not hotel:
            raise HotelNotFound()

        await self.hotel_repo.delete_one(row_id=hotel_id)
        return {
            "message": f"Hotel {hotel_id} deleted successfully"
        }