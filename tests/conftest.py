import pytest_asyncio

from sqlalchemy import select
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies import get_db
from app.models.user import User, UserRole
from app.db.database import Base, AsyncSessionTest, test_async_engine
from tests.data import (
    TEST_USER,
    TEST_LOGIN,
    TEST_ADMIN,
    TEST_ADMIN_LOGIN
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_db():
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with AsyncSessionTest() as db:
        yield db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def override_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionTest() as db:
        yield db
        await db.rollback()


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def authorized_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        await client.post("/auth/register", json=TEST_USER)
        response = await client.post("/auth/login", json=TEST_LOGIN)
        assert response.status_code == 200
        yield client


@pytest_asyncio.fixture
async def admin_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        await client.post("/auth/register", json=TEST_ADMIN)

        async with AsyncSessionTest() as db:
            result = await db.execute(
                select(User).where(User.email == TEST_ADMIN["email"])
            )
            user = result.scalar_one()
            user.role = UserRole.ADMIN
            await db.commit()

        response = await client.post("/auth/login", json=TEST_ADMIN_LOGIN)
        assert response.status_code == 200
        yield client