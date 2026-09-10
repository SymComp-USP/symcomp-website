from datetime import UTC, datetime, timedelta

import jwt
import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.models import RefreshToken
from app.auth.security import create_random_token, hash_token
from app.core.config import Settings, get_settings
from app.core.database import get_session
from app.main import app
from app.users import services as user_services
from app.users.schemas import UserCreate

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


@pytest.fixture
def test_settings() -> Settings:
    settings = get_settings()
    settings.app_env = "dev"
    return settings


@pytest.fixture
def jwt_settings(test_settings: Settings) -> Settings:
    """Alias semântico: settings usados para assinar/decodificar JWTs em testes."""
    return test_settings


# ---------------------------------------------------------------------------
# DB
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# HTTPX clients
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


@pytest.fixture
def user_factory(db_session: AsyncSession):
    """Cria um usuário persistido dentro da sessão de teste."""

    async def _make(
        email: str = "factory-user@example.com",
        name: str = "Factory User",
        password: str = "password123",
    ):
        return await user_services.create_user(
            db_session,
            UserCreate(email=email, name=name, password=password),
        )

    return _make


@pytest.fixture
def expired_refresh_token_factory(db_session: AsyncSession):
    """Cria um refresh token já expirado e retorna a string em claro."""

    async def _make(user_id):
        token_str = create_random_token()
        db_session.add(
            RefreshToken(
                user_id=user_id,
                token_hash=hash_token(token_str),
                expires_at=datetime.now(UTC) - timedelta(seconds=1),
            )
        )
        await db_session.flush()
        return token_str

    return _make


@pytest.fixture
def revoked_refresh_token_factory(db_session: AsyncSession):
    """Cria um refresh token e o revoga, retornando a string em claro."""
    from app.auth import services as auth_services

    async def _make(user_id):
        token_str = await auth_services.create_refresh_token(db_session, user_id)
        await auth_services.revoke_refresh_token(db_session, token_str)
        return token_str

    return _make


@pytest.fixture
def expired_access_token_factory(test_settings: Settings):
    """Gera um access token JWT já expirado, assinado com a chave real."""

    def _make(email: str) -> str:
        payload = {
            "sub": email,
            "exp": datetime.now(UTC) - timedelta(seconds=1),
        }
        return jwt.encode(
            payload,
            test_settings.secret_key.get_secret_value(),
            algorithm=test_settings.token_algorithm,
        )

    return _make


@pytest.fixture
def access_token_without_sub_factory(test_settings: Settings):
    """Gera um access token válido no tempo, mas sem claim 'sub'."""

    def _make() -> str:
        payload = {"exp": datetime.now(UTC) + timedelta(minutes=5)}
        return jwt.encode(
            payload,
            test_settings.secret_key.get_secret_value(),
            algorithm=test_settings.token_algorithm,
        )

    return _make


@pytest.fixture
def access_token_wrong_signature_factory(test_settings: Settings):
    """Gera um JWT assinado com outra chave."""

    def _make(email: str) -> str:
        payload = {
            "sub": email,
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        }
        return jwt.encode(
            payload,
            "wrong-large-secret-key-foo-bar-eez",
            algorithm=test_settings.token_algorithm,
        )

    return _make
