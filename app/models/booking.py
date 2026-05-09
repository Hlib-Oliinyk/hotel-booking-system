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

    def validate_dates(self) -> None:
        if self.check_in >= self.check_out:
            raise ValueError("Дата заїзду має бути раніше дати виїзду")

    def calculate_total_cost(self, price_per_night: int) -> int:
        self.validate_dates()
        return (self.check_out - self.check_in).days * price_per_night

    def is_cancelled(self) -> bool:
        return self.status == "cancelled"

    def cancel(self) -> None:
        if self.is_cancelled():
            raise ValueError("Booking is already cancelled")
        self.status = "cancelled"