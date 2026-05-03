import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.db import Base, get_async_session
import random

# Асинхронная тестовая БД SQLite in-memory
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_async_session():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    import asyncio
    # Импортируем модели здесь, чтобы они зарегистрировались в Base.metadata
    from app import models  # включает все модели
    async def create():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(create())
    yield
    async def drop():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await test_engine.dispose()
    asyncio.run(drop())


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_user_data():
    unique_id = random.randint(1000, 9999)
    return {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "testpass123"
    }


@pytest.fixture
def auth_token(client, test_user_data):
    reg = client.post("/auth/register", json=test_user_data)
    assert reg.status_code == 201, reg.text
    login = client.post("/auth/login", data={
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    })
    assert login.status_code == 200, login.text
    return login.json()["access_token"]
