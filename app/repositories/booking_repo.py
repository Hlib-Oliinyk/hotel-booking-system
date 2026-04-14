from sqlalchemy import select, and_, func

from app.models.booking import Booking
from app.repositories.base import BaseRepository


class BookingRepository(BaseRepository):
    model = Booking

    async def get_booked_count(self, room_id: int, check_in, check_out):
        query = (
            select(func.count(Booking.id))
            .where(
                and_(
                    Booking.room_id == room_id,
                    Booking.check_in < check_out,
                    Booking.check_out > check_in,
                    Booking.status != "cancelled"
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0