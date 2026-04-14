from typing import Self
from datetime import date
from pydantic import BaseModel, model_validator, ConfigDict


class BookingBase(BaseModel):
    room_id: int
    check_in: date
    check_out: date


class BookingCreate(BaseModel):
    hotel_id: int
    room_number: str
    check_in: date
    check_out: date

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.check_in >= self.check_out:
            raise ValueError("Check-out date must be after check-in date")
        if self.check_in < date.today():
            raise ValueError("Check-in date cannot be in the past")
        return self


class BookingResponse(BookingBase):
    id: int
    user_id: int
    total_cost: int
    status: str
    model_config = ConfigDict(from_attributes=True)