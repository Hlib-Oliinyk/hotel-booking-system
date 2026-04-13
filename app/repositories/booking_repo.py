from app.models.booking import Booking
from app.repositories.base import BaseRepository


class BookingRepository(BaseRepository):
    model = Booking