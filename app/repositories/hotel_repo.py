from sqlalchemy import select, or_

from app.models.hotel import Hotel
from app.repositories.base import BaseRepository


class HotelRepository(BaseRepository):
    model = Hotel

    async def get_filtered_hotels(
        self,
        search: str | None = None,
        location: str | None = None,
        stars: int | None = None
    ):
        query = select(self.model)

        if search:
            query = query.filter(
                or_(
                    self.model.title.icontains(search),
                    self.model.location.icontains(search)
                )
            )
        elif location:
            query = query.filter(self.model.location.icontains(location))

        if stars:
            query = query.filter(self.model.stars == stars)

        result = await self.db.execute(query)
        return result.scalars().all()