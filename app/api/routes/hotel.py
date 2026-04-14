from typing import Annotated
from fastapi import APIRouter, Depends

from app.models.user import User
from app.services.hotel_service import HotelService
from app.schemas.hotel import HotelResponse, HotelCreate
from app.dependencies import get_current_admin_user, get_hotel_service


router = APIRouter(
    prefix="/hotel",
    tags=["Hotel"]
)

@router.post("/", response_model=HotelResponse)
async def create_hotel(
    hotel_data: HotelCreate,
    admin_user: Annotated[User, Depends(get_current_admin_user)],
    hotel_service: Annotated[HotelService, Depends(get_hotel_service)]
):
    return await hotel_service.add_hotel(hotel_data)


@router.get("/", response_model=list[HotelResponse])
async def get_hotels(
    hotel_service: Annotated[HotelService, Depends(get_hotel_service)],
    location: str | None = None
):
    return await hotel_service.get_all_hotels(location)


@router.put("/{hotel_id}", response_model=HotelResponse)
async def update_hotel(
    hotel_id: int,
    hotel_data: HotelCreate,
    admin_user: Annotated[User, Depends(get_current_admin_user)],
    hotel_service: Annotated[HotelService, Depends(get_hotel_service)]
):
    return await hotel_service.update_hotel(hotel_id, hotel_data)

@router.delete("/{hotel_id}")
async def delete_hotel(
    hotel_id: int,
    admin_user: Annotated[User, Depends(get_current_admin_user)],
    hotel_service: Annotated[HotelService, Depends(get_hotel_service)]
):
    return await hotel_service.delete_hotel(hotel_id)