from fastapi.responses import JSONResponse
from app.utils.exceptions.base import AppError

def setup_exception_handler(app):
    @app.exception_handler(AppError)
    async def app_error_handler(request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )