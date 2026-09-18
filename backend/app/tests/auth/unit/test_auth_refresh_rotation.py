from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import services as auth_services
from app.auth.scopes import DEFAULT_SCOPES, Scope
from app.core.exceptions.app_errors import UnauthorizedError

# ===========================================================================
# Rotação básica
# ===========================================================================


@pytest.mark.asyncio
async def test_rotation_revokes_old_token_and_creates_new(
    db_session: AsyncSession, user_factory, refresh_token_factory, refresh_token_repo
):
    user = await user_factory(email="rot-basic@example.com")
    old_token = await refresh_token_factory(user.id)

    result = await auth_services.refresh_access_token(db_session, old_token)

    # Devemos ter exatamente 2 tokens no banco: o antigo (revogado) e o novo.
    tokens = await refresh_token_repo.all_for_user(user.id)
    assert len(tokens) == 2

    old_row = await refresh_token_repo.get_by_plaintext(old_token)
    assert old_row is not None
    assert old_row.revoked_at is not None

    new_row = await refresh_token_repo.get_by_plaintext(result.refresh_token)
    assert new_row is not None
    assert new_row.revoked_at is None
    assert new_row.user_id == user.id


@pytest.mark.asyncio
async def test_rotation_returns_new_refresh_string_distinct_from_old(
    db_session: AsyncSession, user_factory, refresh_token_factory
):
    user = await user_factory(email="rot-distinct@example.com")
    old_token = await refresh_token_factory(user.id)

    result = await auth_services.refresh_access_token(db_session, old_token)

    assert result.refresh_token != old_token
    assert len(result.refresh_token) > 0


@pytest.mark.asyncio
async def test_rotation_returns_a_usable_access_token(
    db_session: AsyncSession, user_factory, refresh_token_factory, jwt_settings
):
    user = await user_factory(email="rot-access@example.com")
    old_token = await refresh_token_factory(user.id)

    result = await auth_services.refresh_access_token(db_session, old_token)

    import jwt

    payload = jwt.decode(
        result.access_token,
        jwt_settings.secret_key.get_secret_value(),
        algorithms=[jwt_settings.token_algorithm],
    )
    assert payload["sub"] == str(user.id)


# ===========================================================================
# Reuso do token antigo
# ===========================================================================


@pytest.mark.asyncio
async def test_old_token_cannot_be_reused_after_rotation(
    db_session: AsyncSession, user_factory, refresh_token_factory
):
    user = await user_factory(email="rot-reuse@example.com")
    old_token = await refresh_token_factory(user.id)

    await auth_services.refresh_access_token(db_session, old_token)

    with pytest.raises(UnauthorizedError):
        await auth_services.refresh_access_token(db_session, old_token)


@pytest.mark.asyncio
async def test_chain_of_rotations_works(
    db_session: AsyncSession, user_factory, refresh_token_factory
):
    user = await user_factory(email="rot-chain@example.com")
    token = await refresh_token_factory(user.id)

    for _ in range(5):
        result = await auth_services.refresh_access_token(db_session, token)
        token = result.refresh_token

    # O último token deve ser válido
    result = await auth_services.refresh_access_token(db_session, token)
    assert result.refresh_token is not None


# ===========================================================================
# Scopes
# ===========================================================================


@pytest.mark.asyncio
async def test_rotation_preserves_scopes_by_default(
    db_session: AsyncSession, user_factory, refresh_token_factory, jwt_settings
):
    user = await user_factory(email="rot-scopes@example.com")
    token = await refresh_token_factory(user.id, [Scope.OPENID, Scope.PROFILE])

    result = await auth_services.refresh_access_token(db_session, token)

    import jwt

    payload = jwt.decode(
        result.access_token,
        jwt_settings.secret_key.get_secret_value(),
        algorithms=[jwt_settings.token_algorithm],
    )
    assert set(payload["scopes"].split(" ")) == {"openid", "profile"}


@pytest.mark.asyncio
async def test_rotation_allows_narrowing(
    db_session: AsyncSession, user_factory, refresh_token_factory, jwt_settings
):
    user = await user_factory(email="rot-narrow@example.com")
    token = await refresh_token_factory(user.id, list(DEFAULT_SCOPES))

    result = await auth_services.refresh_access_token(
        db_session, token, requested_scopes=[Scope.OPENID, Scope.PROFILE]
    )

    import jwt

    payload = jwt.decode(
        result.access_token,
        jwt_settings.secret_key.get_secret_value(),
        algorithms=[jwt_settings.token_algorithm],
    )
    assert set(payload["scopes"].split(" ")) == {"openid", "profile"}

    # O NOVO refresh token também deve ter os scopes narrowados
    result2 = await auth_services.refresh_access_token(db_session, result.refresh_token)
    payload2 = jwt.decode(
        result2.access_token,
        jwt_settings.secret_key.get_secret_value(),
        algorithms=[jwt_settings.token_algorithm],
    )
    assert set(payload2["scopes"].split(" ")) == {"openid", "profile"}


@pytest.mark.asyncio
async def test_rotation_rejects_scope_escalation(
    db_session: AsyncSession, user_factory, refresh_token_factory
):
    user = await user_factory(email="rot-escalate@example.com")
    token = await refresh_token_factory(user.id, [Scope.OPENID, Scope.PROFILE])

    with pytest.raises(UnauthorizedError):
        await auth_services.refresh_access_token(
            db_session, token, requested_scopes=list(DEFAULT_SCOPES)
        )


# ===========================================================================
# Estados inválidos
# ===========================================================================


@pytest.mark.asyncio
async def test_rotation_rejects_unknown_token(db_session: AsyncSession):
    with pytest.raises(UnauthorizedError):
        await auth_services.refresh_access_token(db_session, "does-not-exist")


@pytest.mark.asyncio
async def test_rotation_rejects_expired_token(
    db_session: AsyncSession, user_factory, expired_refresh_token_factory
):
    user = await user_factory(email="rot-exp@example.com")
    token = await expired_refresh_token_factory(user.id)

    with pytest.raises(UnauthorizedError):
        await auth_services.refresh_access_token(db_session, token)


@pytest.mark.asyncio
async def test_rotation_rejects_already_revoked_token(
    db_session: AsyncSession, user_factory, revoked_refresh_token_factory
):
    user = await user_factory(email="rot-rev@example.com")
    token = await revoked_refresh_token_factory(user.id)

    with pytest.raises(UnauthorizedError):
        await auth_services.refresh_access_token(db_session, token)


@pytest.mark.asyncio
async def test_rotation_rejects_deleted_user(
    db_session: AsyncSession, user_factory, refresh_token_factory
):
    user = await user_factory(email="rot-del@example.com")
    token = await refresh_token_factory(user.id)

    user.deleted_at = datetime.now(UTC)
    await db_session.flush()

    with pytest.raises(UnauthorizedError):
        await auth_services.refresh_access_token(db_session, token)
