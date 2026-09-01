import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings, get_settings
from app.core.database import get_session
from app.main import app


@pytest.fixture
def test_settings() -> Settings:
    settings = get_settings()
    settings.app_env = "dev"
    return settings


@pytest_asyncio.fixture
async def db_session(test_settings: Settings):
    db_url = str(test_settings.database_url)

    engine = create_async_engine(db_url)
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
