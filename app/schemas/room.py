from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class RoomBase(BaseModel):
    number: str
    room_type: str
    price_per_night: int = Field(gt=0, description="Price must be greater than zero")
    description: Optional[str] = None


class RoomCreate(RoomBase):
    hotel_id: int


class RoomUpdate(BaseModel):
    number: Optional[str] = None
    room_type: Optional[str] = None
    price_per_night: Optional[int] = Field(None, gt=0)
    description: Optional[str] = None
    is_available: Optional[bool] = None


class RoomResponse(RoomBase):
    id: int
    hotel_id: int
    is_available: bool
    model_config = ConfigDict(from_attributes=True)