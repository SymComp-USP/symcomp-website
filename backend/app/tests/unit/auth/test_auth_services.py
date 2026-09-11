from datetime import UTC, datetime

import jwt
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import services as auth_services
from app.auth.models import RefreshToken
from app.auth.scopes import DEFAULT_SCOPES, Scope
from app.auth.security import hash_token
from app.core.config import Settings
from app.core.exceptions.app_errors import UnauthorizedError


def _decode_access(token: str, settings: Settings) -> dict:
    """Decodifica um access_token (sem aud)."""
    return jwt.decode(
        token,
        settings.secret_key.get_secret_value(),
        algorithms=[settings.token_algorithm],
    )


def _decode_id(token: str, settings: Settings) -> dict:
    """Decodifica um id_token, exigindo a audience esperada."""
    return jwt.decode(
        token,
        settings.secret_key.get_secret_value(),
        algorithms=[settings.token_algorithm],
        audience=settings.audience,
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


def test_create_access_token_has_sub_scopes_exp_iat(jwt_settings: Settings):
    # não usa DB; user_id fake
    import uuid

    user_id = uuid.uuid4()
    token = auth_services.create_access_token(user_id, [Scope.PROFILE, Scope.EMAIL])

    payload = _decode_access(token, jwt_settings)

    assert payload["sub"] == str(user_id)
    assert payload["scopes"] == "profile email"
    assert "exp" in payload
    assert "iat" in payload


def test_create_access_token_with_empty_scopes(jwt_settings: Settings):
    import uuid

    user_id = uuid.uuid4()
    token = auth_services.create_access_token(user_id, [])

    payload = _decode_access(token, jwt_settings)

    assert payload["scopes"] == ""


# ===========================================================================
# create_id_token
# ===========================================================================


@pytest.mark.asyncio
async def test_create_id_token_returns_none_without_openid_scope(
    db_session: AsyncSession, user_factory
):
    user = await user_factory(email="id-no-openid@example.com")

    result = await auth_services.create_id_token(
        db_session, [Scope.PROFILE, Scope.EMAIL], user.id
    )

    assert result is None


@pytest.mark.asyncio
async def test_create_id_token_with_openid_only(
    db_session: AsyncSession, user_factory, jwt_settings: Settings
):
    user = await user_factory(email="id-openid@example.com")

    token = await auth_services.create_id_token(db_session, [Scope.OPENID], user.id)

    assert token is not None
    payload = _decode_id(token, jwt_settings)

    assert payload["sub"] == str(user.id)
    assert payload["iss"] == str(jwt_settings.issuer)
    assert payload["aud"] == jwt_settings.audience
    assert "iat" in payload
    assert "exp" in payload
    # Não deve incluir claims de email/profile
    assert "email" not in payload
    assert "name" not in payload


@pytest.mark.asyncio
async def test_create_id_token_includes_email_claim(
    db_session: AsyncSession, user_factory, jwt_settings: Settings
):
    user = await user_factory(email="id-email@example.com")

    token = await auth_services.create_id_token(
        db_session, [Scope.OPENID, Scope.EMAIL], user.id
    )
    payload = _decode_id(token, jwt_settings)

    assert payload["email"] == user.email


@pytest.mark.asyncio
async def test_create_id_token_includes_profile_claims(
    db_session: AsyncSession, user_factory, jwt_settings: Settings
):
    user = await user_factory(email="id-profile@example.com", name="Profile User")

    token = await auth_services.create_id_token(
        db_session, [Scope.OPENID, Scope.PROFILE], user.id
    )
    payload = _decode_id(token, jwt_settings)

    assert payload["name"] == "Profile User"
    assert payload["is_verified"] is False
    assert "created_at" in payload
    assert "updated_at" in payload


@pytest.mark.asyncio
async def test_create_id_token_with_all_scopes(
    db_session: AsyncSession, user_factory, jwt_settings: Settings
):
    user = await user_factory(email="id-all@example.com", name="Full User")

    token = await auth_services.create_id_token(
        db_session, list(DEFAULT_SCOPES), user.id
    )
    payload = _decode_id(token, jwt_settings)

    assert payload["email"] == user.email
    assert payload["name"] == "Full User"


# ===========================================================================
# create_refresh_token
# ===========================================================================


@pytest.mark.asyncio
async def test_create_refresh_token_persists_hashed_token_and_scopes(
    db_session: AsyncSession, user_factory
):
    user = await user_factory(email="refresh-create@example.com")
    scopes = [Scope.OPENID, Scope.PROFILE]

    token = await auth_services.create_refresh_token(db_session, user.id, scopes)

    assert isinstance(token, str) and len(token) > 0

    stored = (
        await db_session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == hash_token(token))
        )
    ).scalar_one()

    assert stored.user_id == user.id
    assert stored.revoked_at is None
    assert stored.expires_at > datetime.now(UTC)
    assert stored.scopes == "openid profile"


# ===========================================================================
# refresh_access_token
# ===========================================================================


@pytest.mark.asyncio
async def test_refresh_access_token_returns_new_access_token(
    db_session: AsyncSession, user_factory, jwt_settings: Settings
):
    user = await user_factory(email="refresh-ok@example.com")
    token = await auth_services.create_refresh_token(
        db_session, user.id, list(DEFAULT_SCOPES)
    )

    new_access = await auth_services.refresh_access_token(db_session, token)

    payload = _decode_access(new_access, jwt_settings)
    assert payload["sub"] == str(user.id)
    assert set(payload["scopes"].split(" ")) == set(DEFAULT_SCOPES)


@pytest.mark.asyncio
async def test_refresh_access_token_rejects_unknown_token(db_session: AsyncSession):
    with pytest.raises(UnauthorizedError):
        await auth_services.refresh_access_token(db_session, "does-not-exist")


@pytest.mark.asyncio
async def test_refresh_access_token_rejects_expired_token(
    db_session: AsyncSession, user_factory, expired_refresh_token_factory
):
    user = await user_factory(email="refresh-exp@example.com")
    token = await expired_refresh_token_factory(user.id)

    with pytest.raises(UnauthorizedError):
        await auth_services.refresh_access_token(db_session, token)


@pytest.mark.asyncio
async def test_refresh_access_token_rejects_revoked_token(
    db_session: AsyncSession, user_factory, revoked_refresh_token_factory
):
    user = await user_factory(email="refresh-rev@example.com")
    token = await revoked_refresh_token_factory(user.id)

    with pytest.raises(UnauthorizedError):
        await auth_services.refresh_access_token(db_session, token)


@pytest.mark.asyncio
async def test_refresh_access_token_rejects_deleted_user(
    db_session: AsyncSession, user_factory
):
    user = await user_factory(email="refresh-del@example.com")
    token = await auth_services.create_refresh_token(
        db_session, user.id, list(DEFAULT_SCOPES)
    )

    user.deleted_at = datetime.now(UTC)
    await db_session.flush()

    with pytest.raises(UnauthorizedError):
        await auth_services.refresh_access_token(db_session, token)


@pytest.mark.asyncio
async def test_refresh_access_token_narrowing_is_allowed(
    db_session: AsyncSession, user_factory, jwt_settings: Settings
):
    user = await user_factory(email="refresh-narrow@example.com")
    token = await auth_services.create_refresh_token(
        db_session, user.id, [Scope.OPENID, Scope.PROFILE, Scope.EMAIL]
    )

    new_access = await auth_services.refresh_access_token(
        db_session, token, requested_scopes=[Scope.OPENID, Scope.PROFILE]
    )

    payload = _decode_access(new_access, jwt_settings)
    assert set(payload["scopes"].split(" ")) == {"openid", "profile"}


@pytest.mark.asyncio
async def test_refresh_access_token_rejects_scope_escalation(
    db_session: AsyncSession, user_factory
):
    user = await user_factory(email="refresh-escalate@example.com")
    token = await auth_services.create_refresh_token(
        db_session, user.id, [Scope.OPENID, Scope.PROFILE]
    )

    with pytest.raises(UnauthorizedError):
        await auth_services.refresh_access_token(
            db_session,
            token,
            requested_scopes=[Scope.OPENID, Scope.PROFILE, Scope.EMAIL],
        )


@pytest.mark.asyncio
async def test_refresh_access_token_uses_original_scopes_when_not_specified(
    db_session: AsyncSession, user_factory, jwt_settings: Settings
):
    user = await user_factory(email="refresh-original@example.com")
    token = await auth_services.create_refresh_token(
        db_session, user.id, [Scope.OPENID, Scope.EMAIL]
    )

    new_access = await auth_services.refresh_access_token(db_session, token)

    payload = _decode_access(new_access, jwt_settings)
    assert set(payload["scopes"].split(" ")) == {"openid", "email"}


# ===========================================================================
# revoke_refresh_token
# ===========================================================================


@pytest.mark.asyncio
async def test_revoke_refresh_token_marks_as_revoked(
    db_session: AsyncSession, user_factory
):
    user = await user_factory(email="revoke-ok@example.com")
    token = await auth_services.create_refresh_token(
        db_session, user.id, list(DEFAULT_SCOPES)
    )

    await auth_services.revoke_refresh_token(db_session, token)

    with pytest.raises(UnauthorizedError):
        await auth_services.refresh_access_token(db_session, token)


@pytest.mark.asyncio
async def test_revoke_unknown_token_is_noop(db_session: AsyncSession):
    await auth_services.revoke_refresh_token(db_session, "no-such-token")


@pytest.mark.asyncio
async def test_revoke_is_idempotent(db_session: AsyncSession, user_factory):
    user = await user_factory(email="revoke-idem@example.com")
    token = await auth_services.create_refresh_token(
        db_session, user.id, list(DEFAULT_SCOPES)
    )

    await auth_services.revoke_refresh_token(db_session, token)
    await auth_services.revoke_refresh_token(db_session, token)


# ===========================================================================
# build_refresh_token_cookie
# ===========================================================================


def test_build_refresh_token_cookie_shape(jwt_settings: Settings):
    cookie = auth_services.build_refresh_token_cookie("my-token")

    assert cookie["key"] == "refresh_token"
    assert cookie["value"] == "my-token"
    assert cookie["httponly"] is True
    assert cookie["secure"] is True
    assert cookie["samesite"] == "lax"
    assert cookie["max_age"] == jwt_settings.refresh_token_expire_days * 24 * 60 * 60
