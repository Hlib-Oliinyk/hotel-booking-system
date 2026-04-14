from sqlalchemy import select, update
from datetime import datetime, timezone, timedelta

from app.repositories.base import BaseRepository
from app.models.refresh_token import RefreshToken


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
        return await self.add_one(data)

    async def rotate_token_data(
        self,
        old_token_id: int,
        user_id: int,
        new_token_hash: str
    ) -> RefreshToken:
        await self.update_one(old_token_id, {"is_revoked": True})

        return await self.add_one({
            "user_id": user_id,
            "token": new_token_hash,
            "expired_at": datetime.now(timezone.utc) + timedelta(days=14)
        })

    async def delete_token(self, token_hash: str):
        stmt = update(RefreshToken).where(RefreshToken.token == token_hash).values(is_revoked=True)
        await self.db.execute(stmt)
