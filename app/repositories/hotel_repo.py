from sqlalchemy import select

from app.models.hotel import Hotel
from app.repositories.base import BaseRepository


class HotelRepository(BaseRepository):
    model = Hotel

    async def get_filtered_hotels(self, location: str | None = None, stars: int | None = None):
        query = select(self.model)

        if location:
            query = query.filter(self.model.location.icontains(location))
        if stars:
            query = query.filter(self.model.stars == stars)

        result = await self.db.execute(query)
        return result.scalars().all()