from fastapi import APIRouter

from .routes.auth import router as auth_router
from .routes.hotel import router as hotel_router


router = APIRouter()

router.include_router(auth_router)
router.include_router(hotel_router)