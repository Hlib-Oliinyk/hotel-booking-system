from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class RoomBase(BaseModel):
    number: str
    room_type: str
    price_per_night: int = Field(gt=0, description="Price must be greater than zero")
    description: Optional[str] = None


class RoomCreate(RoomBase):
    pass


class RoomResponse(RoomBase):
    id: int
    is_available: bool
    model_config = ConfigDict(from_attributes=True)