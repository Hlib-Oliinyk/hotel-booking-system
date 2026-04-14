from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Hotel(Base):
    __tablename__ = "hotels"

    title: Mapped[str] = mapped_column(nullable=False)
    location: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    stars: Mapped[int] = mapped_column(nullable=True)

    rooms: Mapped[list["Room"]] = relationship(back_populates="hotel")