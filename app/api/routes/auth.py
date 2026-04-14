from typing import Annotated
from fastapi import APIRouter, Depends, Response, Request

from app.models.user import User
from app.securities.hashing import hash_token
from app.services.user_service import UserService
from app.services.token_service import TokenService
from app.utils.exceptions.token import InvalidCredentials
from app.securities.authorization.jwt import jwt_generator
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.dependencies import get_user_service, get_token_service, get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)]
):
    user = await service.get_user(current_user.id)
    return user


@router.post("/register", response_model=UserResponse)
async def register(
    data: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)]
):
    user = await service.create_user(data)
    return user


@router.post("/login")
async def login(
    data: UserLogin,
    response: Response,
    user_service: Annotated[UserService, Depends(get_user_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)]
):
    user = await user_service.authenticate_user(data.email, data.password)

    access_token = jwt_generator.generate_access_token(user)
    refresh_token = token_service.create_refresh_token()
    refresh_token_hash = hash_token(refresh_token)

    await token_service.save_new_token(user.id, refresh_token_hash)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 14
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }


@router.delete("/logout")
async def logout(
    request: Request,
    response: Response,
    service: Annotated[TokenService, Depends(get_token_service)]
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is not None:
        await service.delete_refresh_token(refresh_token)

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

    return {
        "detail": "Logged out"
    }


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    service: Annotated[TokenService, Depends(get_token_service)]
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise InvalidCredentials()

    new_refresh_token, new_access_token = await service.rotate_refresh_token(refresh_token)

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesite="lax",
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 14
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "Bearer"
    }