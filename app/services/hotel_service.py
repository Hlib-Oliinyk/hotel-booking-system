from app.schemas.hotel import HotelCreate
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