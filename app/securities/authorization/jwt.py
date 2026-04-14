from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

from app.models.user import User
from app.core.config import settings
from app.utils.exceptions.user import UserNotFound
from app.utils.exceptions.token import InvalidCredentials


class JWTGenerator:
    def __init__(self):
        pass

    def _generate_jwt_token(
        self,
        data: dict,
        expired_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()

        if expired_delta:
            expire = datetime.now(timezone.utc) + expired_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=30)

        to_encode.update({"exp": expire})
        encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encode_jwt

    def generate_access_token(self, user: User) -> str:
        if user is None:
            raise UserNotFound()

        return self._generate_jwt_token(
            data={"sub":str(user.id)}
        )

    def get_details_from_token(self, token: str) -> int:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
            user_id = int(payload.get("sub"))
        except (JWTError, TypeError, ValueError):
            raise InvalidCredentials()

        return user_id


def get_jwt_token() -> JWTGenerator:
    return JWTGenerator()

jwt_generator: JWTGenerator = get_jwt_token()