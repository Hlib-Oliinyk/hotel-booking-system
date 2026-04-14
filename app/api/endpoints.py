from fastapi import APIRouter

from .routes.auth import router as auth_router
from .routes.hotel import router as hotel_router
from .routes.room import router as room_router
from .routes.booking import router as booking_router


router = APIRouter()

router.include_router(auth_router)
router.include_router(hotel_router)
router.include_router(room_router)
router.include_router(booking_router)