import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.users.services as user_services
from app.auth.models import RefreshToken
from app.auth.scopes import Scope
from app.auth.security import (
    create_jwt_token,
    create_random_token,
    hash_token,
    verify_password,
)
from app.core.config import get_settings
from app.core.exceptions.app_errors import UnauthorizedError


async def authenticate(db_session: AsyncSession, email: str, password: str):
    user = await user_services.get_user_by_email(db_session, email)

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def create_access_token(user_id: uuid.UUID, requested_scopes: list[str]):
    settings = get_settings()

    return create_jwt_token(
        {"sub": str(user_id), "scopes": " ".join(requested_scopes)},
        settings.access_token_expire_minutes,
    )


async def create_id_token(
    session: AsyncSession, requested_scopes: list[str], user_id: uuid.UUID
) -> str | None:
    settings = get_settings()

    if Scope.OPENID not in requested_scopes:
        return None

    user = await user_services.get_user_by_id(session, user_id)

    id_token_payload = {
        "sub": str(user.id),
        "iss": settings.issuer.encoded_string(),
        "aud": settings.audience,
        "iat": int(datetime.now(UTC).timestamp()),
    }

    if Scope.EMAIL in requested_scopes:
        id_token_payload["email"] = user.email

    if Scope.PROFILE in requested_scopes:
        id_token_payload["name"] = user.name
        id_token_payload["is_verified"] = user.is_verified
        id_token_payload["created_at"] = user.created_at.isoformat()
        id_token_payload["updated_at"] = user.updated_at.isoformat()

    id_token = create_jwt_token(id_token_payload, settings.access_token_expire_minutes)

    return id_token


async def create_refresh_token(
    session: AsyncSession, user_id: uuid.UUID, requested_scopes: list[str]
):
    settings = get_settings()
    REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

    token_str = create_random_token()

    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=hash_token(token_str),
        expires_at=datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        scopes=" ".join(requested_scopes),
    )

    session.add(refresh_token)
    await session.flush()

    return token_str


async def refresh_access_token(
    session: AsyncSession,
    refresh_token_str: str,
    requested_scopes: list[str] | None = None,
):
    hashed = hash_token(refresh_token_str)

    refresh_token = (
        await session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == hashed)
        )
    ).scalar_one_or_none()

    if refresh_token is None:
        raise UnauthorizedError(detail="Invalid refresh token")

    expires_at = refresh_token.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)

    if expires_at <= datetime.now(UTC):
        raise UnauthorizedError(detail="Invalid refresh token")

    if refresh_token.revoked_at is not None:
        raise UnauthorizedError(detail="Invalid refresh token")

    user = await user_services.get_user_by_id(session, refresh_token.user_id)

    if user is None or user.deleted_at is not None:
        raise UnauthorizedError(detail="Invalid refresh token")

    # Scopes podem ser removidos a partir do refresh token; nunca adicionados.
    original_scopes = refresh_token.scopes.split(" ") if refresh_token.scopes else []

    if requested_scopes is not None:
        if not set(requested_scopes).issubset(set(original_scopes)):
            raise UnauthorizedError(detail="Invalid scopes for refresh")
        scopes = requested_scopes
    else:
        scopes = original_scopes

    return create_access_token(user.id, scopes)


async def revoke_refresh_token(session: AsyncSession, refresh_token_str: str):
    hashed = hash_token(refresh_token_str)

    refresh_token = (
        await session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == hashed)
        )
    ).scalar_one_or_none()

    if refresh_token is None or refresh_token.revoked_at is not None:
        return

    refresh_token.revoked_at = datetime.now(UTC)
    await session.flush()


def build_refresh_token_cookie(refresh_token: str) -> dict:
    REFRESH_EXPIRE_TIME_SECONDS = (
        get_settings().refresh_token_expire_days * 24 * 60 * 60
    )

    return {
        "key": "refresh_token",
        "value": refresh_token,
        "httponly": True,
        "secure": True,
        "samesite": "lax",
        "max_age": REFRESH_EXPIRE_TIME_SECONDS,
    }
