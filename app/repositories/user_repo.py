from pydantic import EmailStr
from sqlalchemy import select, exists

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = User

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.find_one_or_none(id=user_id)

    async def get_by_email(self, user_email: EmailStr) -> User | None:
        return await self.find_one_or_none(email=user_email)

    async def user_exists(self, user_email: EmailStr) -> bool:
        stmt = select(
            exists().where(User.email == user_email)
        )
        result = await self.db.execute(stmt)
        return result.scalar()

    async def create(self, **data) -> User:
        return await self.add_one(data)
