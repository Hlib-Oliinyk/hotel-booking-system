from typing import Annotated
from fastapi import APIRouter, Depends

from app.models.user import User
from app.services.booking_service import BookingService
from app.schemas.booking import BookingCreate, BookingResponse
from app.dependencies import get_booking_service, get_current_user


router = APIRouter(
    prefix="/booking",
    tags=["Bookings"]
)

@router.post("", response_model=BookingResponse)
async def add_booking(
    booking_data: BookingCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    booking_service: Annotated[BookingService, Depends(get_booking_service)]
):
    return await booking_service.create_booking(
        user_id=current_user.id,
        room_id=booking_data.room_id,
        check_in=booking_data.check_in,
        check_out=booking_data.check_out
    )


@router.get("/me", response_model=list[BookingResponse])
async def get_my_bookings(
    current_user: Annotated[User, Depends(get_current_user)],
    booking_service: Annotated[BookingService, Depends(get_booking_service)]
):
    return await booking_service.get_user_bookings(current_user.id)


@router.patch("/{booking_id}", response_model=BookingResponse)
async def cancel_my_booking(
    booking_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    booking_service: Annotated[BookingService, Depends(get_booking_service)]
):
    return await booking_service.cancel_booking(booking_id, current_user.id)