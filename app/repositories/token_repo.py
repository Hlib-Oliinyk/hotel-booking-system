from datetime import datetime, timezone, timedelta

from sqlalchemy import select, update

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class TokenRepository(BaseRepository):
    model = RefreshToken

    async def get_validate_refresh_token(self, token: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(
            RefreshToken.is_revoked == False,
            RefreshToken.token == token,
            RefreshToken.expired_at > datetime.now(timezone.utc)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save_token(self, **data) -> RefreshToken:
        refresh_token = RefreshToken(**data)
        self.db.add(refresh_token)
        await self.db.commit()
        await self.db.refresh(refresh_token)
        return refresh_token

    async def rotate_token_data(
        self,
        old_token_id: int,
        user_id: int,
        new_token_hash: str
    ) -> RefreshToken:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.id == old_token_id)
            .values(is_revoked = True)
        )

        new_refresh_token = RefreshToken(
            user_id=user_id,
            token=new_token_hash,
            expired_at=datetime.now(timezone.utc) + timedelta(days=14)
        )

        self.db.add(new_refresh_token)
        await self.db.commit()
        await self.db.refresh(new_refresh_token)
        return new_refresh_token

    async def delete_token(self, token_hash: str):
        stmt = update(RefreshToken).where(RefreshToken.token == token_hash).values(is_revoked = True)
        await self.db.execute(stmt)
        await self.db.commit()
