from pydantic import BaseModel, ConfigDict


class HotelBase(BaseModel):
    title: str
    location: str
    description: str | None = None
    stars: int | None = None


class HotelCreate(HotelBase):
    pass


class HotelResponse(HotelBase):
    id: int
    model_config = ConfigDict(from_attributes=True)