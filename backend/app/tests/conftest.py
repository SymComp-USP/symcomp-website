from datetime import UTC, datetime

import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings, get_settings
from app.core.database import get_session
from app.main import app
from app.users import services as user_services
from app.users.schemas import UserCreate


@pytest.fixture
def test_settings() -> Settings:
    settings = get_settings()
    settings.app_env = "dev"
    return settings


@pytest.fixture
def jwt_settings(test_settings: Settings) -> Settings:
    return test_settings


@pytest_asyncio.fixture
async def db_session(test_settings: Settings):
    engine = create_async_engine(str(test_settings.database_url))
    TestingSessionLocal = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with engine.connect() as connection:
        transaction = await connection.begin()
        async with TestingSessionLocal(bind=connection) as session:
            yield session
        await transaction.rollback()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_settings: Settings):
    def override_get_settings():
        return test_settings

    app.dependency_overrides[get_settings] = override_get_settings
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def db_client(db_session: AsyncSession, test_settings: Settings):
    async def override_get_session():
        yield db_session

    def override_get_settings():
        return test_settings

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_settings] = override_get_settings
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def user_factory(db_session: AsyncSession):
    async def _make(
        email: str = "factory-user@example.com",
        name: str = "Factory User",
        password: str = "password123",
    ):
        return await user_services.create_user(
            db_session, UserCreate(email=email, name=name, password=password)
        )

    return _make


@pytest.fixture
def deleted_user_factory(db_session: AsyncSession, user_factory):
    async def _make(
        email: str = "deleted-user@example.com",
        name: str = "Deleted User",
        password: str = "password123",
    ):
        user = await user_factory(email=email, name=name, password=password)
        user.deleted_at = datetime.now(UTC)
        await db_session.flush()
        return user

    return _make
