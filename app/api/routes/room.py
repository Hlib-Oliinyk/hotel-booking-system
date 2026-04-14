from typing import Annotated
from fastapi import APIRouter, Depends, status

from app.models.user import User
from app.services.room_service import RoomService
from app.schemas.room import RoomResponse, RoomCreate, RoomUpdate
from app.dependencies import get_room_service, get_current_admin_user


router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)

@router.get("", response_model=list[RoomResponse])
async def get_rooms(
    room_service: Annotated[RoomService, Depends(get_room_service)],
    hotel_id: int | None = None
):
    filters = {"hotel_id": hotel_id} if hotel_id else {}
    return await room_service.get_all_rooms(**filters)


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: int,
    room_service: Annotated[RoomService, Depends(get_room_service)]
):
    return await room_service.get_room_by_id(room_id)


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: RoomCreate,
    admin_user: Annotated[User, Depends(get_current_admin_user)],
    room_service: Annotated[RoomService, Depends(get_room_service)]
):
    return await room_service.create_new_room(room_data)


@router.patch("/{room_id}", response_model=RoomResponse)
async def patch_room(
    room_id: int,
    room_data: RoomUpdate,
    admin_user: Annotated[User, Depends(get_current_admin_user)],
    room_service: Annotated[RoomService, Depends(get_room_service)]
):
    return await room_service.update_room(room_id, room_data)


@router.delete("/{room_id}")
async def delete_room(
    room_id: int,
    admin_user: Annotated[User, Depends(get_current_admin_user)],
    room_service: Annotated[RoomService, Depends(get_room_service)]
):
    return await room_service.delete_room(room_id)