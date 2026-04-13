import enum

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(default=UserRole.CUSTOMER)

    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")