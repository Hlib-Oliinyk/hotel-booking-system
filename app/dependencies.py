from typing import Annotated
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.db.database import AsyncSessionLocal
from app.services.room_service import RoomService
from app.services.user_service import UserService
from app.services.hotel_service import HotelService
from app.services.token_service import TokenService
from app.repositories.room_repo import RoomRepository
from app.repositories.user_repo import UserRepository
from app.services.booking_service import BookingService
from app.repositories.hotel_repo import HotelRepository
from app.repositories.token_repo import TokenRepository
from app.securities.authorization.jwt import jwt_generator
from app.repositories.booking_repo import BookingRepository
from app.utils.exceptions.token import InvalidCredentials
from app.utils.exceptions.user import UserForbidden


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


def get_user_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_hotel_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> HotelRepository:
    return HotelRepository(db)


def get_room_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> RoomRepository:
    return RoomRepository(db)


def get_booking_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> BookingRepository:
    return BookingRepository(db)


def get_token_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> TokenRepository:
    return TokenRepository(db)


def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    return UserService(user_repo)


def get_token_service(
    token_repo: Annotated[TokenRepository, Depends(get_token_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> TokenService:
    return TokenService(token_repo, user_repo)


def get_hotel_service(
    hotel_repo: Annotated[HotelRepository, Depends(get_hotel_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> HotelService:
    return HotelService(hotel_repo, user_repo)


def get_room_service(
    room_repo: Annotated[RoomRepository, Depends(get_room_repository)],
    hotel_repo: Annotated[HotelRepository, Depends(get_hotel_repository)]
) -> RoomService:
    return RoomService(room_repo, hotel_repo)


def get_booking_service(
    booking_repo: Annotated[BookingRepository, Depends(get_booking_repository)],
    room_repo: Annotated[RoomRepository, Depends(get_room_repository)]
) -> BookingService:
    return BookingService(booking_repo, room_repo)

def get_token_from_header_or_cookie(request: Request) -> str:
    # Виправлено: стандарт JWT використовує "Bearer " без двокрапки
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]  # "Bearer " довжина = 7
    
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token
    
    raise InvalidCredentials()

async def get_current_user(
    token: Annotated[str, Depends(get_token_from_header_or_cookie)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    user_id = jwt_generator.get_details_from_token(token)
    user = await user_service.get_user(user_id)
    return user


def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:  # Додано явний тип повернення
    if current_user.role != "admin":
        raise UserForbidden()
    return current_user
