"""Testes dos endpoints de usuário autenticado (/api/v1/user/me)."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import services as auth_services
from app.auth.scopes import Scope
from app.auth.security import verify_password

URL = "/api/v1/user/me"


def _auth(user, scopes=(Scope.PROFILE, Scope.EMAIL)) -> dict[str, str]:
    token = auth_services.create_access_token(user.id, list(scopes))
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Proteção
# ---------------------------------------------------------------------------


async def test_update_name_without_authorization_returns_401(db_client):
    r = await db_client.patch(URL, json={"name": "Novo Nome"})
    assert r.status_code == 401


async def test_update_name_without_profile_scope_returns_401(
    db_client, regular_user, db_session: AsyncSession
):
    original_name = regular_user.name

    r = await db_client.patch(
        URL, json={"name": "Novo Nome"}, headers=_auth(regular_user, [Scope.EMAIL])
    )

    assert r.status_code == 401
    await db_session.refresh(regular_user)
    assert regular_user.name == original_name


async def test_update_name_without_email_scope_returns_401(
    db_client, regular_user, db_session: AsyncSession
):
    original_name = regular_user.name

    r = await db_client.patch(
        URL, json={"name": "Novo Nome"}, headers=_auth(regular_user, [Scope.PROFILE])
    )

    assert r.status_code == 401
    await db_session.refresh(regular_user)
    assert regular_user.name == original_name


async def test_update_name_of_deleted_user_returns_401(db_client, deleted_user_factory):
    deleted = await deleted_user_factory()

    r = await db_client.patch(URL, json={"name": "Novo Nome"}, headers=_auth(deleted))

    assert r.status_code == 401


# ---------------------------------------------------------------------------
# Sucesso
# ---------------------------------------------------------------------------


async def test_user_can_update_own_name(
    db_client, regular_user, db_session: AsyncSession
):
    r = await db_client.patch(
        URL, json={"name": "Ada Lovelace"}, headers=_auth(regular_user)
    )

    assert r.status_code == 200, r.text
    body = r.json()
    assert body["name"] == "Ada Lovelace"
    assert body["id"] == str(regular_user.id)
    assert body["email"] == regular_user.email
    assert "password" not in body and "password_hash" not in body

    await db_session.refresh(regular_user)
    assert regular_user.name == "Ada Lovelace"


async def test_updated_name_is_returned_by_me_endpoint(db_client, regular_user):
    headers = _auth(regular_user)

    await db_client.patch(URL, json={"name": "Grace Hopper"}, headers=headers)
    r = await db_client.get("/api/v1/auth/me", headers=headers)

    assert r.status_code == 200, r.text
    assert r.json()["name"] == "Grace Hopper"


async def test_update_name_strips_surrounding_whitespace(db_client, regular_user):
    r = await db_client.patch(
        URL, json={"name": "   Linus Torvalds  "}, headers=_auth(regular_user)
    )

    assert r.status_code == 200, r.text
    assert r.json()["name"] == "Linus Torvalds"


async def test_update_name_accepts_max_length(db_client, regular_user):
    name = "a" * 255

    r = await db_client.patch(URL, json={"name": name}, headers=_auth(regular_user))

    assert r.status_code == 200, r.text
    assert r.json()["name"] == name


async def test_update_name_does_not_change_other_fields(
    db_client, regular_user, db_session: AsyncSession
):
    email = regular_user.email
    password_hash = regular_user.password_hash

    r = await db_client.patch(
        URL, json={"name": "Outro Nome"}, headers=_auth(regular_user)
    )

    assert r.status_code == 200, r.text
    await db_session.refresh(regular_user)
    assert regular_user.email == email
    assert regular_user.password_hash == password_hash
    assert verify_password("password123", regular_user.password_hash)
    assert regular_user.is_admin is False
    assert regular_user.is_verified is False


# ---------------------------------------------------------------------------
# Validação
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"name": None},
        {"name": ""},
        {"name": "     "},
        {"name": "a" * 256},
        {"name": 123},
    ],
)
async def test_update_name_rejects_invalid_name(
    db_client, regular_user, db_session: AsyncSession, payload
):
    original_name = regular_user.name

    r = await db_client.patch(URL, json=payload, headers=_auth(regular_user))

    assert r.status_code == 422
    await db_session.refresh(regular_user)
    assert regular_user.name == original_name


@pytest.mark.parametrize(
    "extra",
    [
        {"email": "hacker@example.com"},
        {"password": "brand-new-pass"},
        {"is_admin": True},
        {"is_verified": True},
    ],
)
async def test_update_name_rejects_other_fields(
    db_client, regular_user, db_session: AsyncSession, extra
):
    email = regular_user.email
    original_name = regular_user.name

    r = await db_client.patch(
        URL, json={"name": "Novo Nome", **extra}, headers=_auth(regular_user)
    )

    assert r.status_code == 422
    await db_session.refresh(regular_user)
    assert regular_user.email == email
    assert regular_user.name == original_name
    assert regular_user.is_admin is False
    assert regular_user.is_verified is False
