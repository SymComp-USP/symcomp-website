from datetime import UTC, datetime

import jwt
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import services as auth_services
from app.auth.models import RefreshToken
from app.auth.security import hash_token
from app.core.config import Settings
from app.core.exceptions.app_errors import AppError

# ===========================================================================
# helpers
# ===========================================================================


def _decode(token: str, settings: Settings) -> dict:
    return jwt.decode(
        token,
        settings.secret_key.get_secret_value(),
        algorithms=[settings.token_algorithm],
    )


# ===========================================================================
# authenticate
# ===========================================================================


@pytest.mark.asyncio
async def test_authenticate_returns_user_for_valid_credentials(
    db_session: AsyncSession, user_factory
):
    user = await user_factory(email="auth-ok@example.com")

    result = await auth_services.authenticate(db_session, user.email, "password123")

    assert result is not None
    assert result.email == user.email


@pytest.mark.asyncio
async def test_authenticate_rejects_invalid_password(
    db_session: AsyncSession, user_factory
):
    user = await user_factory(email="auth-bad-pass@example.com")

    result = await auth_services.authenticate(db_session, user.email, "wrong")

    assert result is None


@pytest.mark.asyncio
async def test_authenticate_rejects_unknown_email(db_session: AsyncSession):
    result = await auth_services.authenticate(
        db_session, "nobody@example.com", "password123"
    )

    assert result is None


# ===========================================================================
# create_access_token
# ===========================================================================


def test_create_access_token_has_sub_and_future_exp(jwt_settings: Settings):
    token = auth_services.create_access_token({"sub": "x@example.com"})

    payload = _decode(token, jwt_settings)

    assert payload["sub"] == "x@example.com"
    exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
    assert exp > datetime.now(UTC)


# ===========================================================================
# create_refresh_token
# ===========================================================================


@pytest.mark.asyncio
async def test_create_refresh_token_persists_hashed_token(
    db_session: AsyncSession, user_factory
):
    user = await user_factory(email="refresh-create@example.com")

    token = await auth_services.create_refresh_token(db_session, user.id)

    assert isinstance(token, str) and len(token) > 0

    stored = (
        await db_session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == hash_token(token))
        )
    ).scalar_one()

    assert stored.user_id == user.id
    assert stored.revoked_at is None
    assert stored.expires_at > datetime.now(UTC)


# ===========================================================================
# refresh_access_token
# ===========================================================================


@pytest.mark.asyncio
async def test_refresh_access_token_returns_new_access_token(
    db_session: AsyncSession, user_factory, jwt_settings: Settings
):
    user = await user_factory(email="refresh-svc-ok@example.com")
    token = await auth_services.create_refresh_token(db_session, user.id)

    new_access = await auth_services.refresh_access_token(db_session, token)

    payload = _decode(new_access, jwt_settings)
    assert payload["sub"] == user.email


@pytest.mark.asyncio
async def test_refresh_access_token_rejects_unknown_token(db_session: AsyncSession):
    with pytest.raises(AppError, match="Invalid refresh token"):
        await auth_services.refresh_access_token(db_session, "does-not-exist")


@pytest.mark.asyncio
async def test_refresh_access_token_rejects_expired_token(
    db_session: AsyncSession, user_factory, expired_refresh_token_factory
):
    user = await user_factory(email="refresh-svc-exp@example.com")
    token = await expired_refresh_token_factory(user.id)

    with pytest.raises(AppError, match="Invalid refresh token"):
        await auth_services.refresh_access_token(db_session, token)


@pytest.mark.asyncio
async def test_refresh_access_token_rejects_revoked_token(
    db_session: AsyncSession, user_factory, revoked_refresh_token_factory
):
    user = await user_factory(email="refresh-svc-rev@example.com")
    token = await revoked_refresh_token_factory(user.id)

    with pytest.raises(AppError, match="Invalid refresh token"):
        await auth_services.refresh_access_token(db_session, token)


@pytest.mark.asyncio
async def test_refresh_access_token_rejects_deleted_user(
    db_session: AsyncSession, user_factory
):
    user = await user_factory(email="refresh-svc-del@example.com")
    token = await auth_services.create_refresh_token(db_session, user.id)

    user.deleted_at = datetime.now(UTC)
    await db_session.flush()

    with pytest.raises(AppError, match="Invalid refresh token"):
        await auth_services.refresh_access_token(db_session, token)


# ===========================================================================
# revoke_refresh_token
# ===========================================================================


@pytest.mark.asyncio
async def test_revoke_refresh_token_marks_as_revoked(
    db_session: AsyncSession, user_factory
):
    user = await user_factory(email="revoke-ok@example.com")
    token = await auth_services.create_refresh_token(db_session, user.id)

    await auth_services.revoke_refresh_token(db_session, token)

    with pytest.raises(AppError):
        await auth_services.refresh_access_token(db_session, token)


@pytest.mark.asyncio
async def test_revoke_unknown_token_is_noop(db_session: AsyncSession):
    # não deve levantar exceção
    await auth_services.revoke_refresh_token(db_session, "no-such-token")


@pytest.mark.asyncio
async def test_revoke_is_idempotent(db_session: AsyncSession, user_factory):
    user = await user_factory(email="revoke-idem@example.com")
    token = await auth_services.create_refresh_token(db_session, user.id)

    await auth_services.revoke_refresh_token(db_session, token)
    await auth_services.revoke_refresh_token(db_session, token)
