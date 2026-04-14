from fastapi import FastAPI

from app.api.endpoints import router
from app.exceptions_handler import setup_exception_handler


app = FastAPI(
    docs_url="/api/docs",
)

app.include_router(router)
setup_exception_handler(app)

@app.get("/")
def root():
    return {
        "project": "hotel-booking-system",
        "docs": "/api/docs"
    }