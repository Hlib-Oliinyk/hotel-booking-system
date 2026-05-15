from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.api.endpoints import router
from app.exceptions_handler import setup_exception_handler

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(docs_url="/api/docs")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(router)
setup_exception_handler(app)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/hotels", response_class=HTMLResponse)
async def hotels_page(request: Request):
    return templates.TemplateResponse(request, "hotels.html")


@app.get("/hotels/{hotel_id}", response_class=HTMLResponse)
async def hotel_detail_page(request: Request, hotel_id: int):
    return templates.TemplateResponse(request, "hotel_detail.html", {"hotel_id": hotel_id})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    return templates.TemplateResponse(request, "profile.html")


@app.get("/profile/bookings", response_class=HTMLResponse)
async def profile_bookings_page(request: Request):
    return templates.TemplateResponse(request, "profile_bookings.html")


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse(request, "admin.html")