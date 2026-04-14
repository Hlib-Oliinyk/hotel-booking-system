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
from app.repositories.hotel_repo import HotelRepository
from app.repositories.token_repo import TokenRepository
from app.securities.authorization.jwt import jwt_generator
from app.exceptions_handler import InvalidCredentials, UserForbidden


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


def get_user_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    return UserService(UserRepository(db))


def get_token_service(db: Annotated[AsyncSession, Depends(get_db)]) -> TokenService:
    return TokenService(TokenRepository(db), UserRepository(db))


async def get_hotel_service(db: AsyncSession = Depends(get_db)) -> HotelService:
    return HotelService(HotelRepository(db))


async def get_room_service(db: AsyncSession = Depends(get_db)) -> RoomService:
    return RoomService(RoomRepository(db), HotelRepository(db))


def get_token_from_header_or_cookie(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer: "):
        return auth_header[7:]

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


async def get_current_admin_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role != "admin":
        raise UserForbidden()
    return current_user