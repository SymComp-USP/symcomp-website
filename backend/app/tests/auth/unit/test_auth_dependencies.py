import uuid

import pytest
from fastapi.security import SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import services as auth_services
from app.auth.dependencies import (
    get_current_user,
    get_current_user_including_deleted,
)
from app.auth.scopes import DEFAULT_SCOPES, Scope
from app.core.config import Settings
from app.core.exceptions.app_errors import UnauthorizedError

# ===========================================================================
# get_current_user_including_deleted — caminho feliz
# ===========================================================================


@pytest.mark.asyncio
async def test_returns_user_for_valid_token(
    db_session: AsyncSession, user_factory, test_settings: Settings
):
    user = await user_factory(email="inc-ok@example.com")
    token = auth_services.create_access_token(user.id, [Scope.PROFILE, Scope.EMAIL])
    security_scopes = SecurityScopes(scopes=[Scope.PROFILE])

    result = await get_current_user_including_deleted(
        db_session, token, security_scopes, test_settings
    )

    assert result.id == user.id


@pytest.mark.asyncio
async def test_returns_deleted_user_when_called_directly(
    db_session: AsyncSession, deleted_user_factory, test_settings: Settings
):
    user = await deleted_user_factory(email="inc-deleted@example.com")
    token = auth_services.create_access_token(user.id, list(DEFAULT_SCOPES))
    security_scopes = SecurityScopes(scopes=[])

    result = await get_current_user_including_deleted(
        db_session, token, security_scopes, test_settings
    )

    assert result.id == user.id
    assert result.deleted_at is not None


# ===========================================================================
# get_current_user_including_deleted — falhas
# ===========================================================================


@pytest.mark.asyncio
async def test_rejects_garbage_token(db_session: AsyncSession, test_settings: Settings):
    security_scopes = SecurityScopes(scopes=[])

    with pytest.raises(UnauthorizedError):
        await get_current_user_including_deleted(
            db_session, "not-a-jwt", security_scopes, test_settings
        )


@pytest.mark.asyncio
async def test_rejects_wrong_signature(
    db_session: AsyncSession,
    user_factory,
    access_token_wrong_signature_factory,
    test_settings: Settings,
):
    user = await user_factory(email="inc-wrong-sig@example.com")
    token = access_token_wrong_signature_factory(user.id)
    security_scopes = SecurityScopes(scopes=[])

    with pytest.raises(UnauthorizedError):
        await get_current_user_including_deleted(
            db_session, token, security_scopes, test_settings
        )


@pytest.mark.asyncio
async def test_rejects_expired_token(
    db_session: AsyncSession,
    user_factory,
    expired_access_token_factory,
    test_settings: Settings,
):
    user = await user_factory(email="inc-exp@example.com")
    token = expired_access_token_factory(user.id)
    security_scopes = SecurityScopes(scopes=[])

    with pytest.raises(UnauthorizedError):
        await get_current_user_including_deleted(
            db_session, token, security_scopes, test_settings
        )


@pytest.mark.asyncio
async def test_rejects_token_without_sub(
    db_session: AsyncSession,
    access_token_without_sub_factory,
    test_settings: Settings,
):
    token = access_token_without_sub_factory()
    security_scopes = SecurityScopes(scopes=[])

    with pytest.raises(UnauthorizedError):
        await get_current_user_including_deleted(
            db_session, token, security_scopes, test_settings
        )


@pytest.mark.asyncio
async def test_rejects_token_without_scopes(
    db_session: AsyncSession,
    user_factory,
    access_token_without_scopes_factory,
    test_settings: Settings,
):
    user = await user_factory(email="inc-no-scopes@example.com")
    token = access_token_without_scopes_factory(user.id)
    security_scopes = SecurityScopes(scopes=[])

    with pytest.raises(UnauthorizedError):
        await get_current_user_including_deleted(
            db_session, token, security_scopes, test_settings
        )


@pytest.mark.asyncio
async def test_rejects_unknown_user(db_session: AsyncSession, test_settings: Settings):
    token = auth_services.create_access_token(uuid.uuid4(), list(DEFAULT_SCOPES))
    security_scopes = SecurityScopes(scopes=[])

    with pytest.raises(UnauthorizedError):
        await get_current_user_including_deleted(
            db_session, token, security_scopes, test_settings
        )


@pytest.mark.asyncio
async def test_rejects_when_required_scope_missing(
    db_session: AsyncSession, user_factory, test_settings: Settings
):
    user = await user_factory(email="inc-missing-scope@example.com")
    token = auth_services.create_access_token(user.id, [Scope.PROFILE])
    security_scopes = SecurityScopes(scopes=[Scope.PROFILE, Scope.EMAIL])

    with pytest.raises(UnauthorizedError):
        await get_current_user_including_deleted(
            db_session, token, security_scopes, test_settings
        )


# ===========================================================================
# get_current_user
# ===========================================================================


@pytest.mark.asyncio
async def test_get_current_user_accepts_active_user(user_factory):
    user = await user_factory(email="cur-active@example.com")

    result = await get_current_user(user)

    assert result.id == user.id


@pytest.mark.asyncio
async def test_get_current_user_rejects_deleted_user(deleted_user_factory):
    user = await deleted_user_factory(email="cur-deleted@example.com")

    with pytest.raises(UnauthorizedError):
        await get_current_user(user)
