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
