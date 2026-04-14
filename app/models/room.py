from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Room(Base):
    __tablename__ = "rooms"

    number: Mapped[str] = mapped_column(unique=True, nullable=False)
    room_type: Mapped[str] = mapped_column(nullable=False)
    price_per_night: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    is_available: Mapped[bool] = mapped_column(default=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"), nullable=False)

    bookings: Mapped[list["Booking"]] = relationship(back_populates="room")
    hotel: Mapped["Hotel"] = relationship(back_populates="rooms")