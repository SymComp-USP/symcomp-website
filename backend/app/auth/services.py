import uuid
from datetime import UTC, datetime, timedelta

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.users.services as user_services
from app.auth.models import RefreshToken
from app.auth.security import (
    create_random_token,
    hash_token,
    verify_password,
)
from app.core.config import get_settings
from app.core.exceptions.app_errors import BadRequestError, UnauthorizedError


async def authenticate(db_session: AsyncSession, email: str, password: str):
    user = await user_services.get_user_by_email(db_session, email)

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def create_access_token(data: dict):
    settings = get_settings()

    SECRET_KEY = settings.secret_key.get_secret_value()
    TOKEN_ALGORITHM = settings.token_algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=TOKEN_ALGORITHM)
    return encoded_jwt


async def create_refresh_token(session: AsyncSession, user_id: uuid.UUID):
    settings = get_settings()
    REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

    token_str = create_random_token()

    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=hash_token(token_str),
        expires_at=datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    session.add(refresh_token)
    await session.flush()

    return token_str


async def refresh_access_token(session: AsyncSession, refresh_token_str: str):
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

    if user is None:
        raise UnauthorizedError(detail="Invalid refresh token")

    if user.deleted_at is not None:
        raise BadRequestError(detail="Inactive user")

    return create_access_token({"sub": user.email})


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
