from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken
from app.auth.scopes import DEFAULT_SCOPES
from app.auth.security import create_random_token, hash_token
from app.core.config import Settings


@pytest.fixture
def expired_refresh_token_factory(db_session: AsyncSession):
    async def _make(user_id: UUID, scopes: list[str] | None = None):
        token_str = create_random_token()
        db_session.add(
            RefreshToken(
                user_id=user_id,
                token_hash=hash_token(token_str),
                expires_at=datetime.now(UTC) - timedelta(seconds=1),
                scopes=" ".join(scopes or DEFAULT_SCOPES),
            )
        )
        await db_session.flush()
        return token_str

    return _make


@pytest.fixture
def revoked_refresh_token_factory(db_session: AsyncSession):
    from app.auth import services as auth_services

    async def _make(user_id: UUID, scopes: list[str] | None = None):
        token_str = await auth_services.create_refresh_token(
            db_session, user_id, scopes or DEFAULT_SCOPES
        )
        await auth_services.revoke_refresh_token(db_session, token_str)
        return token_str

    return _make


def _encode(claims: dict, settings: Settings) -> str:
    return jwt.encode(
        claims,
        settings.secret_key.get_secret_value(),
        algorithm=settings.token_algorithm,
    )


@pytest.fixture
def expired_access_token_factory(test_settings: Settings):
    def _make(user_id: UUID, scopes: list[str] | None = None) -> str:
        return _encode(
            {
                "sub": str(user_id),
                "scopes": " ".join(scopes or DEFAULT_SCOPES),
                "exp": int((datetime.now(UTC) - timedelta(seconds=1)).timestamp()),
            },
            test_settings,
        )

    return _make


@pytest.fixture
def access_token_without_sub_factory(test_settings: Settings):
    def _make(scopes: list[str] | None = None) -> str:
        return _encode(
            {
                "scopes": " ".join(scopes or DEFAULT_SCOPES),
                "exp": int((datetime.now(UTC) + timedelta(minutes=5)).timestamp()),
            },
            test_settings,
        )

    return _make


@pytest.fixture
def access_token_without_scopes_factory(test_settings: Settings):
    def _make(user_id: UUID) -> str:
        return _encode(
            {
                "sub": str(user_id),
                "exp": int((datetime.now(UTC) + timedelta(minutes=5)).timestamp()),
            },
            test_settings,
        )

    return _make


@pytest.fixture
def access_token_wrong_signature_factory(test_settings: Settings):
    def _make(user_id: UUID, scopes: list[str] | None = None) -> str:
        return jwt.encode(
            {
                "sub": str(user_id),
                "scopes": " ".join(scopes or DEFAULT_SCOPES),
                "exp": int((datetime.now(UTC) + timedelta(minutes=5)).timestamp()),
            },
            "a-completely-different-and-long-secret",
            algorithm=test_settings.token_algorithm,
        )

    return _make
