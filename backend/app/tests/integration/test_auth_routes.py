from datetime import UTC, datetime

import pytest
from httpx2 import AsyncClient

from app.auth import services as auth_services

# ===========================================================================
# POST /api/v1/auth/login
# ===========================================================================


@pytest.mark.asyncio
async def test_login_returns_access_token_and_sets_refresh_cookie(
    db_client: AsyncClient, user_factory
):
    user = await user_factory(email="login-ok@example.com")

    response = await db_client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "password123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert response.cookies.get("refresh_token")


@pytest.mark.asyncio
async def test_login_with_wrong_password_returns_401(
    db_client: AsyncClient, user_factory
):
    user = await user_factory(email="login-wrong-pass@example.com")

    response = await db_client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert "refresh_token" not in response.cookies


@pytest.mark.asyncio
async def test_login_with_unknown_email_returns_401(db_client: AsyncClient):
    response = await db_client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "whatever"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_missing_fields_returns_422(db_client: AsyncClient):
    response = await db_client.post("/api/v1/auth/login", data={"username": "x"})
    assert response.status_code == 422


# ===========================================================================
# POST /api/v1/auth/refresh
# ===========================================================================


@pytest.mark.asyncio
async def test_refresh_returns_new_access_token_for_valid_cookie(
    db_client: AsyncClient, db_session, user_factory
):
    user = await user_factory(email="refresh-ok@example.com")
    token = await auth_services.create_refresh_token(db_session, user.id)

    db_client.cookies.set("refresh_token", token)
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
async def test_refresh_with_expired_token_returns_401(
    db_client: AsyncClient, user_factory, expired_refresh_token_factory
):
    user = await user_factory(email="refresh-expired@example.com")
    token = await expired_refresh_token_factory(user.id)

    db_client.cookies.set("refresh_token", token)
    response = await db_client.post("/api/v1/auth/refresh")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_revoked_token_returns_401(
    db_client: AsyncClient, user_factory, revoked_refresh_token_factory
):
    user = await user_factory(email="refresh-revoked@example.com")
    token = await revoked_refresh_token_factory(user.id)

    db_client.cookies.set("refresh_token", token)
    response = await db_client.post("/api/v1/auth/refresh")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_for_deleted_user_returns_401(
    db_client: AsyncClient, db_session, user_factory
):
    user = await user_factory(email="refresh-deleted@example.com")
    token = await auth_services.create_refresh_token(db_session, user.id)

    user.deleted_at = datetime.now(UTC)
    await db_session.flush()

    db_client.cookies.set("refresh_token", token)
    response = await db_client.post("/api/v1/auth/refresh")

    assert response.status_code == 401


# ===========================================================================
# POST /api/v1/auth/logout
# ===========================================================================


@pytest.mark.asyncio
async def test_logout_revokes_cookie_refresh_token(
    db_client: AsyncClient, db_session, user_factory
):
    user = await user_factory(email="logout-ok@example.com")
    refresh_token = await auth_services.create_refresh_token(db_session, user.id)

    db_client.cookies.set("refresh_token", refresh_token)
    response = await db_client.post("/api/v1/auth/logout")

    assert response.status_code == 204

    # o token não pode mais ser usado
    db_client.cookies.set("refresh_token", refresh_token)
    retry = await db_client.post("/api/v1/auth/refresh")
    assert retry.status_code == 401


@pytest.mark.asyncio
async def test_logout_without_cookie_returns_204(db_client: AsyncClient):
    response = await db_client.post("/api/v1/auth/logout")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_logout_with_unknown_token_returns_204(db_client: AsyncClient):
    db_client.cookies.set("refresh_token", "garbage-token")
    response = await db_client.post("/api/v1/auth/logout")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_logout_is_idempotent(db_client: AsyncClient, db_session, user_factory):
    user = await user_factory(email="logout-idem@example.com")
    refresh_token = await auth_services.create_refresh_token(db_session, user.id)

    db_client.cookies.set("refresh_token", refresh_token)
    first = await db_client.post("/api/v1/auth/logout")
    second = await db_client.post("/api/v1/auth/logout")

    assert first.status_code == 204
    assert second.status_code == 204


# ===========================================================================
# GET /api/v1/auth/me
# ===========================================================================


@pytest.mark.asyncio
async def test_me_returns_current_user(db_client: AsyncClient, user_factory):
    user = await user_factory(email="me-ok@example.com")
    access_token = auth_services.create_access_token({"sub": user.email})

    response = await db_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == user.email
    assert body["name"] == user.name
    assert body["id"] == str(user.id)


@pytest.mark.asyncio
async def test_me_without_authorization_returns_401(db_client: AsyncClient):
    response = await db_client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_garbage_token_returns_401(db_client: AsyncClient):
    response = await db_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not.a.jwt"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_wrong_signature_returns_401(
    db_client: AsyncClient, user_factory, access_token_wrong_signature_factory
):
    user = await user_factory(email="me-wrong-sig@example.com")
    token = access_token_wrong_signature_factory(user.email)

    response = await db_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_expired_token_returns_401(
    db_client: AsyncClient, user_factory, expired_access_token_factory
):
    user = await user_factory(email="me-expired@example.com")
    token = expired_access_token_factory(user.email)

    response = await db_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_token_without_sub_returns_401(
    db_client: AsyncClient, access_token_without_sub_factory
):
    token = access_token_without_sub_factory()

    response = await db_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_for_deleted_user_returns_401(
    db_client: AsyncClient, db_session, user_factory
):
    user = await user_factory(email="me-deleted@example.com")
    access_token = auth_services.create_access_token({"sub": user.email})

    user.deleted_at = datetime.now(UTC)
    await db_session.flush()

    response = await db_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 401
