from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import services as auth_services
from app.auth.dependencies import get_current_active_user, get_current_user
from app.core.exceptions.app_errors import AppError

# ===========================================================================
# get_current_user
# ===========================================================================


@pytest.mark.asyncio
async def test_get_current_user_returns_user_for_valid_token(
    db_session: AsyncSession, user_factory, test_settings
):
    user = await user_factory(email="cur-ok@example.com")
    token = auth_services.create_access_token({"sub": user.email})

    result = await get_current_user(db_session, token, test_settings)

    assert result.id == user.id
    assert result.email == user.email


@pytest.mark.asyncio
async def test_get_current_user_rejects_garbage(
    db_session: AsyncSession, test_settings
):
    with pytest.raises(AppError) as exc:
        await get_current_user(db_session, "not-a-jwt", test_settings)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_rejects_wrong_signature(
    db_session: AsyncSession,
    user_factory,
    access_token_wrong_signature_factory,
    test_settings,
):
    user = await user_factory(email="cur-wrong@example.com")
    token = access_token_wrong_signature_factory(user.email)

    with pytest.raises(AppError) as exc:
        await get_current_user(db_session, token, test_settings)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_rejects_expired_token(
    db_session: AsyncSession,
    user_factory,
    expired_access_token_factory,
    test_settings,
):
    user = await user_factory(email="cur-exp@example.com")
    token = expired_access_token_factory(user.email)

    with pytest.raises(AppError) as exc:
        await get_current_user(db_session, token, test_settings)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_rejects_token_without_sub(
    db_session: AsyncSession, access_token_without_sub_factory, test_settings
):
    token = access_token_without_sub_factory()

    with pytest.raises(AppError) as exc:
        await get_current_user(db_session, token, test_settings)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_rejects_unknown_user(
    db_session: AsyncSession, test_settings
):
    token = auth_services.create_access_token({"sub": "ghost@example.com"})

    with pytest.raises(AppError) as exc:
        await get_current_user(db_session, token, test_settings)

    assert exc.value.status_code == 401


# ===========================================================================
# get_current_active_user
# ===========================================================================


@pytest.mark.asyncio
async def test_get_current_active_user_returns_active_user(user_factory):
    user = await user_factory(email="active@example.com")

    result = await get_current_active_user(user)

    assert result.id == user.id


@pytest.mark.asyncio
async def test_get_current_active_user_rejects_deleted_user(
    db_session: AsyncSession, user_factory
):
    user = await user_factory(email="inactive@example.com")
    user.deleted_at = datetime.now(UTC)
    await db_session.flush()

    with pytest.raises(AppError) as exc:
        await get_current_active_user(user)

    assert exc.value.status_code == 400
    assert "Inactive user" in exc.value.detail
