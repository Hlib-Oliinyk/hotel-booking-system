from datetime import date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    check_in: Mapped[date] = mapped_column(nullable=False)
    check_out: Mapped[date] = mapped_column(nullable=False)
    total_cost: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(default="pending")

    user: Mapped["User"] = relationship(back_populates="bookings")
    room: Mapped["Room"] = relationship(back_populates="bookings")