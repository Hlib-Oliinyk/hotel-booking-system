import secrets

from datetime import datetime, timezone, timedelta

from app.securities.hashing import hash_token
from app.models.refresh_token import RefreshToken
from app.repositories.user_repo import UserRepository
from app.repositories.token_repo import TokenRepository
from app.utils.exceptions.token import InvalidCredentials
from app.securities.authorization.jwt import jwt_generator


class TokenService:
    def __init__(self, repo: TokenRepository, user_repo: UserRepository):
        self.repo = repo
        self.user_repo = user_repo

    def create_refresh_token(self) -> str:
        return secrets.token_urlsafe(64)

    async def get_validate_refresh_token(self, token: str) -> RefreshToken:
        refresh_token = await self.repo.get_validate_refresh_token(token)
        if refresh_token is None:
            raise InvalidCredentials()
        return refresh_token

    async def save_new_token(self, user_id: int, token_hash: str) -> RefreshToken:
        return await self.repo.save_token(
            user_id = user_id,
            token = token_hash,
            expired_at=datetime.now(timezone.utc) + timedelta(days=14)
        )

    async def rotate_refresh_token(self, token: str) -> tuple[str, str]:
        token_hash = hash_token(token)

        old_token = await self.repo.get_validate_refresh_token(token_hash)
        if old_token is None:
            raise InvalidCredentials()

        new_refresh_token = self.create_refresh_token()
        new_refresh_token_hash = hash_token(new_refresh_token)

        await self.repo.rotate_token_data(
            old_token.id,
            old_token.user_id,
            new_refresh_token_hash
        )

        user = await self.user_repo.get_by_id(old_token.user_id)
        new_access_token = jwt_generator.generate_access_token(user)
        return new_refresh_token, new_access_token

    async def delete_refresh_token(self, token: str):
        token_hash = hash_token(token)
        await self.repo.delete_token(token_hash)