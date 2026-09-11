import pytest
from httpx2 import AsyncClient

from app.auth import services as auth_services
from app.auth.scopes import DEFAULT_SCOPES, Scope

# ===========================================================================
# POST /api/v1/auth/login
# ===========================================================================


@pytest.mark.asyncio
async def test_login_returns_tokens_and_sets_refresh_cookie(
    db_client: AsyncClient, user_factory
):
    user = await user_factory(email="login-ok@example.com")

    response = await db_client.post(
        "/api/v1/auth/login",
        data={
            "username": user.email,
            "password": "password123",
            "scope": "openid profile email",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["id_token"] is not None
    assert body["token_type"] == "bearer"
    assert response.cookies.get("refresh_token")


@pytest.mark.asyncio
async def test_login_without_openid_scope_returns_no_id_token(
    db_client: AsyncClient, user_factory
):
    user = await user_factory(email="login-no-openid@example.com")

    response = await db_client.post(
        "/api/v1/auth/login",
        data={
            "username": user.email,
            "password": "password123",
            "scope": "profile email",
        },
    )

    assert response.status_code == 200
    assert response.json()["id_token"] is None


@pytest.mark.asyncio
async def test_login_with_wrong_password_returns_401(
    db_client: AsyncClient, user_factory
):
    user = await user_factory(email="login-wrong-pass@example.com")

    response = await db_client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "wrong"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_unknown_email_returns_401(db_client: AsyncClient):
    response = await db_client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "whatever"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_unknown_scope_returns_401(
    db_client: AsyncClient, user_factory
):
    user = await user_factory(email="login-bad-scope@example.com")

    response = await db_client.post(
        "/api/v1/auth/login",
        data={
            "username": user.email,
            "password": "password123",
            "scope": "openid admin",
        },
    )

    assert response.status_code == 401


# ===========================================================================
# GET /api/v1/auth/me
# ===========================================================================


@pytest.mark.asyncio
async def test_me_returns_current_user(db_client: AsyncClient, user_factory):
    user = await user_factory(email="me-ok@example.com", name="Me User")
    token = auth_services.create_access_token(user.id, [Scope.PROFILE, Scope.EMAIL])

    response = await db_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == user.email
    assert body["name"] == "Me User"


@pytest.mark.asyncio
async def test_me_without_authorization_returns_401(db_client: AsyncClient):
    response = await db_client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_missing_scope_returns_401(db_client: AsyncClient, user_factory):
    user = await user_factory(email="me-missing-scope@example.com")
    # Só tem "profile", mas /me exige profile + email
    token = auth_services.create_access_token(user.id, [Scope.PROFILE])

    response = await db_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_deleted_user_returns_401(
    db_client: AsyncClient, deleted_user_factory
):
    user = await deleted_user_factory(email="me-deleted@example.com")
    token = auth_services.create_access_token(user.id, [Scope.PROFILE, Scope.EMAIL])

    response = await db_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


# ===========================================================================
# POST /api/v1/auth/refresh
# ===========================================================================


@pytest.mark.asyncio
async def test_refresh_returns_new_access_token(
    db_client: AsyncClient, db_session, user_factory
):
    user = await user_factory(email="refresh-ok@example.com")
    refresh_token = await auth_services.create_refresh_token(
        db_session, user.id, list(DEFAULT_SCOPES)
    )

    db_client.cookies.set("refresh_token", refresh_token)
    response = await db_client.post("/api/v1/auth/refresh")

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_without_cookie_returns_401(db_client: AsyncClient):
    response = await db_client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_unknown_token_returns_401(db_client: AsyncClient):
    db_client.cookies.set("refresh_token", "not-a-real-token")
    response = await db_client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_narrowing_is_accepted(
    db_client: AsyncClient, db_session, user_factory
):
    user = await user_factory(email="refresh-narrow@example.com")
    refresh_token = await auth_services.create_refresh_token(
        db_session, user.id, list(DEFAULT_SCOPES)
    )

    db_client.cookies.set("refresh_token", refresh_token)
    response = await db_client.post(
        "/api/v1/auth/refresh",
        json={"requested_scopes": ["openid", "profile"]},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_refresh_with_scope_escalation_returns_401(
    db_client: AsyncClient, db_session, user_factory
):
    user = await user_factory(email="refresh-escalate@example.com")
    refresh_token = await auth_services.create_refresh_token(
        db_session, user.id, [Scope.OPENID, Scope.PROFILE]
    )

    db_client.cookies.set("refresh_token", refresh_token)
    response = await db_client.post(
        "/api/v1/auth/refresh",
        json={"requested_scopes": ["openid", "profile", "email"]},
    )

    assert response.status_code == 401


# ===========================================================================
# POST /api/v1/auth/logout
# ===========================================================================


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(
    db_client: AsyncClient, db_session, user_factory
):
    user = await user_factory(email="logout-ok@example.com")
    refresh_token = await auth_services.create_refresh_token(
        db_session, user.id, list(DEFAULT_SCOPES)
    )

    db_client.cookies.set("refresh_token", refresh_token)
    response = await db_client.post("/api/v1/auth/logout")

    assert response.status_code == 204

    # Reutilizar o cookie não deve funcionar
    db_client.cookies.set("refresh_token", refresh_token)
    retry = await db_client.post("/api/v1/auth/refresh")
    assert retry.status_code == 401


@pytest.mark.asyncio
async def test_logout_without_cookie_returns_204(db_client: AsyncClient):
    response = await db_client.post("/api/v1/auth/logout")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_logout_with_unknown_token_returns_204(db_client: AsyncClient):
    db_client.cookies.set("refresh_token", "garbage")
    response = await db_client.post("/api/v1/auth/logout")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_logout_is_idempotent(db_client: AsyncClient, db_session, user_factory):
    user = await user_factory(email="logout-idem@example.com")
    refresh_token = await auth_services.create_refresh_token(
        db_session, user.id, list(DEFAULT_SCOPES)
    )

    db_client.cookies.set("refresh_token", refresh_token)
    first = await db_client.post("/api/v1/auth/logout")
    second = await db_client.post("/api/v1/auth/logout")

    assert first.status_code == 204
    assert second.status_code == 204


# ===========================================================================
# POST /api/v1/auth/refresh — ROTAÇÃO
# ===========================================================================


@pytest.mark.asyncio
async def test_refresh_rotates_cookie(
    db_client: AsyncClient, refresh_token_factory, user_factory
):
    """O cookie de refresh deve mudar a cada chamada de /refresh."""
    user = await user_factory(email="refresh-rotate@example.com")
    old_token = await refresh_token_factory(user.id)

    db_client.cookies.set("refresh_token", old_token)
    response = await db_client.post("/api/v1/auth/refresh")

    assert response.status_code == 200
    new_token = response.cookies.get("refresh_token")
    assert new_token is not None
    assert new_token != old_token


@pytest.mark.asyncio
async def test_refresh_old_token_rejected_after_rotation(
    db_client: AsyncClient, refresh_token_factory, user_factory
):
    user = await user_factory(email="refresh-old-rej@example.com")
    old_token = await refresh_token_factory(user.id)

    # 1º refresh — sucesso
    db_client.cookies.set("refresh_token", old_token)
    first = await db_client.post("/api/v1/auth/refresh")
    assert first.status_code == 200

    # 2º refresh com o MESMO cookie antigo — deve falhar
    db_client.cookies.set("refresh_token", old_token)
    second = await db_client.post("/api/v1/auth/refresh")
    assert second.status_code == 401


@pytest.mark.asyncio
async def test_refresh_chain_five_rotations(
    db_client: AsyncClient, refresh_token_factory, user_factory
):
    user = await user_factory(email="refresh-chain@example.com")
    token = await refresh_token_factory(user.id)

    for _ in range(5):
        db_client.cookies.set("refresh_token", token)
        response = await db_client.post("/api/v1/auth/refresh")
        assert response.status_code == 200
        token = response.cookies.get("refresh_token")
        assert token is not None


@pytest.mark.asyncio
async def test_refresh_rotation_response_has_no_id_token(
    db_client: AsyncClient, refresh_token_factory, user_factory
):
    """Refresh não deve emitir id_token (só access)."""
    user = await user_factory(email="refresh-no-idt@example.com")
    token = await refresh_token_factory(user.id)

    db_client.cookies.set("refresh_token", token)
    response = await db_client.post("/api/v1/auth/refresh")

    assert response.status_code == 200
    assert response.json()["id_token"] is None


@pytest.mark.asyncio
async def test_refresh_rotation_updates_cookie_max_age(
    db_client: AsyncClient, refresh_token_factory, user_factory
):
    """O novo cookie deve ter Set-Cookie com max_age definido."""
    user = await user_factory(email="refresh-maxage@example.com")
    token = await refresh_token_factory(user.id)

    db_client.cookies.set("refresh_token", token)
    response = await db_client.post("/api/v1/auth/refresh")

    set_cookie = response.headers.get("set-cookie", "")
    assert "refresh_token=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "Max-Age=" in set_cookie


# ===========================================================================
# ROTAÇÃO + scopes
# ===========================================================================


@pytest.mark.asyncio
async def test_refresh_rotation_narrowing_persists_in_new_token(
    db_client: AsyncClient, refresh_token_factory, user_factory
):
    """Após narrowing, o novo refresh token deve manter os scopes reduzidos."""
    user = await user_factory(email="refresh-narrow-persist@example.com")
    token = await refresh_token_factory(user.id, list(DEFAULT_SCOPES))

    # 1º refresh com narrowing
    db_client.cookies.set("refresh_token", token)
    first = await db_client.post(
        "/api/v1/auth/refresh",
        json={"requested_scopes": ["openid", "profile"]},
    )
    assert first.status_code == 200
    narrowed_token = first.cookies.get("refresh_token")

    # 2º refresh SEM narrowing — deve usar os scopes narrowados do token atual
    db_client.cookies.set("refresh_token", narrowed_token)
    second = await db_client.post("/api/v1/auth/refresh")

    assert second.status_code == 200

    # 3º refresh pedindo "email" — deve falhar (o token atual não tem)
    db_client.cookies.set("refresh_token", second.cookies.get("refresh_token"))
    third = await db_client.post(
        "/api/v1/auth/refresh",
        json={"requested_scopes": ["openid", "profile", "email"]},
    )
    assert third.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rotation_scope_escalation_returns_401(
    db_client: AsyncClient, refresh_token_factory, user_factory
):
    user = await user_factory(email="refresh-escalate@example.com")
    token = await refresh_token_factory(user.id, [Scope.OPENID, Scope.PROFILE])

    db_client.cookies.set("refresh_token", token)
    response = await db_client.post(
        "/api/v1/auth/refresh",
        json={"requested_scopes": ["openid", "profile", "email"]},
    )

    assert response.status_code == 401


# ===========================================================================
# ROTAÇÃO + logout
# ===========================================================================


@pytest.mark.asyncio
async def test_logout_after_rotation_revokes_current_token(
    db_client: AsyncClient, refresh_token_factory, user_factory
):
    user = await user_factory(email="logout-after-rot@example.com")
    token = await refresh_token_factory(user.id)

    # Rotaciona
    db_client.cookies.set("refresh_token", token)
    rotated = await db_client.post("/api/v1/auth/refresh")
    new_token = rotated.cookies.get("refresh_token")

    # Logout com o token novo
    db_client.cookies.set("refresh_token", new_token)
    logout = await db_client.post("/api/v1/auth/logout")
    assert logout.status_code == 204

    # Refresh com o token rotacionado e depois revogado deve falhar
    db_client.cookies.set("refresh_token", new_token)
    retry = await db_client.post("/api/v1/auth/refresh")
    assert retry.status_code == 401


# ===========================================================================
# ROTAÇÃO + estados inválidos
# ===========================================================================


@pytest.mark.asyncio
async def test_refresh_rotation_expired_token_returns_401(
    db_client: AsyncClient, expired_refresh_token_factory, user_factory
):
    user = await user_factory(email="rot-expired@example.com")
    token = await expired_refresh_token_factory(user.id)

    db_client.cookies.set("refresh_token", token)
    response = await db_client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rotation_deleted_user_returns_401(
    db_client: AsyncClient, refresh_token_factory, deleted_user_factory
):
    user = await deleted_user_factory(email="rot-deleted@example.com")
    token = await refresh_token_factory(user.id)

    db_client.cookies.set("refresh_token", token)
    response = await db_client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


# ===========================================================================
# Verificação no banco via app — não vaza token em claro
# ===========================================================================


@pytest.mark.asyncio
async def test_refresh_does_not_store_plaintext_token(
    db_client: AsyncClient, db_session, refresh_token_factory, user_factory
):
    """O novo token NUNCA deve estar em claro no banco (só hash)."""
    from sqlalchemy import select

    from app.auth.models import RefreshToken

    user = await user_factory(email="rot-no-plaintext@example.com")
    token = await refresh_token_factory(user.id)

    db_client.cookies.set("refresh_token", token)
    response = await db_client.post("/api/v1/auth/refresh")
    new_plaintext = response.cookies.get("refresh_token")

    rows = (
        (
            await db_session.execute(
                select(RefreshToken).where(RefreshToken.user_id == user.id)
            )
        )
        .scalars()
        .all()
    )
    stored_values = {row.token_hash for row in rows}

    assert new_plaintext not in stored_values
    assert token not in stored_values
