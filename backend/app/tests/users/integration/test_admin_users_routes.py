"""Testes dos endpoints de admin de usuários (/api/v1/admin/users)."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import verify_password

BASE = "/api/v1/admin/users"


# ---------------------------------------------------------------------------
# Proteção
# ---------------------------------------------------------------------------


async def test_unauthenticated_requests_are_rejected(db_client):
    r = await db_client.get(f"{BASE}/")
    assert r.status_code == 401


@pytest.mark.parametrize(
    "method, path, body",
    [
        (
            "POST",
            "/",
            {"email": "n@example.com", "name": "N", "password": "password123"},
        ),
        ("GET", "/", None),
        ("GET", f"/{uuid.uuid4()}", None),
        ("PATCH", f"/{uuid.uuid4()}", {"name": "X"}),
        ("DELETE", f"/{uuid.uuid4()}", None),
    ],
)
async def test_non_admin_is_forbidden(as_user, regular_user, method, path, body):
    c = as_user(regular_user)
    r = await c.request(method, f"{BASE}{path}", json=body)
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


async def test_admin_can_create_user_with_defaults(as_user, admin_user):
    c = as_user(admin_user)
    r = await c.post(
        f"{BASE}/",
        json={"email": "new@example.com", "name": "New", "password": "password123"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"] == "new@example.com"
    assert body["is_admin"] is False
    assert body["is_verified"] is False
    assert "password" not in body and "password_hash" not in body


async def test_admin_can_create_user_overriding_privileges(
    as_user, admin_user, db_session: AsyncSession
):
    c = as_user(admin_user)
    r = await c.post(
        f"{BASE}/",
        json={
            "email": "boss@example.com",
            "name": "Boss",
            "password": "password123",
            "is_admin": True,
            "is_verified": True,
        },
    )
    assert r.status_code == 201, r.text
    assert r.json()["is_admin"] is True
    assert r.json()["is_verified"] is True


async def test_admin_create_user_with_existing_email_fails(
    as_user, admin_user, regular_user
):
    c = as_user(admin_user)
    r = await c.post(
        f"{BASE}/",
        json={"email": regular_user.email, "name": "Dup", "password": "password123"},
    )
    assert r.status_code == 400
    assert r.json()["type"] == "user_already_exists"


async def test_admin_create_user_validates_payload(as_user, admin_user):
    c = as_user(admin_user)
    r = await c.post(
        f"{BASE}/", json={"email": "not-an-email", "name": "X", "password": "short"}
    )
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


async def test_admin_can_list_users_paginated(as_user, admin_user, user_factory):
    await user_factory(email="l1@example.com")
    await user_factory(email="l2@example.com")
    c = as_user(admin_user)

    r = await c.get(f"{BASE}/", params={"limit": 2, "offset": 0})

    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["items"]) == 2
    assert body["limit"] == 2
    assert body["offset"] == 0
    assert body["total"] >= 3

    r = await c.get(f"{BASE}/", params={"limit": 2, "offset": 2})
    assert r.status_code == 200
    assert r.json()["offset"] == 2


async def test_list_rejects_invalid_pagination(as_user, admin_user):
    c = as_user(admin_user)
    r = await c.get(f"{BASE}/", params={"limit": 0})
    assert r.status_code == 422


async def test_list_hides_deleted_users_unless_requested(
    as_user, admin_user, deleted_user_factory
):
    deleted = await deleted_user_factory()
    c = as_user(admin_user)

    r = await c.get(f"{BASE}/", params={"limit": 100})
    assert str(deleted.id) not in {u["id"] for u in r.json()["items"]}

    r = await c.get(f"{BASE}/", params={"limit": 100, "include_deleted": True})
    assert str(deleted.id) in {u["id"] for u in r.json()["items"]}


# ---------------------------------------------------------------------------
# Get
# ---------------------------------------------------------------------------


async def test_admin_can_get_user(as_user, admin_user, regular_user):
    c = as_user(admin_user)
    r = await c.get(f"{BASE}/{regular_user.id}")
    assert r.status_code == 200, r.text
    assert r.json()["id"] == str(regular_user.id)
    assert r.json()["deleted_at"] is None


async def test_admin_can_get_deleted_user(as_user, admin_user, deleted_user_factory):
    deleted = await deleted_user_factory()
    c = as_user(admin_user)
    r = await c.get(f"{BASE}/{deleted.id}")
    assert r.status_code == 200, r.text
    assert r.json()["deleted_at"] is not None


async def test_get_unknown_user_returns_404(as_user, admin_user):
    c = as_user(admin_user)
    r = await c.get(f"{BASE}/{uuid.uuid4()}")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


async def test_admin_can_update_user_fields(as_user, admin_user, regular_user):
    c = as_user(admin_user)
    r = await c.patch(
        f"{BASE}/{regular_user.id}",
        json={"name": "Renamed", "email": "renamed@example.com"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["name"] == "Renamed"
    assert r.json()["email"] == "renamed@example.com"


async def test_admin_can_override_privileges(as_user, admin_user, regular_user):
    c = as_user(admin_user)

    r = await c.patch(
        f"{BASE}/{regular_user.id}", json={"is_admin": True, "is_verified": True}
    )
    assert r.status_code == 200, r.text
    assert r.json()["is_admin"] is True
    assert r.json()["is_verified"] is True

    r = await c.patch(f"{BASE}/{regular_user.id}", json={"is_admin": False})
    assert r.json()["is_admin"] is False
    assert r.json()["is_verified"] is True  # não enviado, não alterado


async def test_admin_can_reset_user_password(
    as_user, admin_user, regular_user, db_session: AsyncSession
):
    c = as_user(admin_user)
    r = await c.patch(f"{BASE}/{regular_user.id}", json={"password": "brand-new-pass"})
    assert r.status_code == 200, r.text

    await db_session.refresh(regular_user)
    assert verify_password("brand-new-pass", regular_user.password_hash)


async def test_patch_ignores_null_fields(as_user, admin_user, regular_user):
    c = as_user(admin_user)
    r = await c.patch(
        f"{BASE}/{regular_user.id}", json={"name": None, "is_admin": None}
    )
    assert r.status_code == 200, r.text
    assert r.json()["name"] == regular_user.name
    assert r.json()["is_admin"] is False


async def test_patch_with_email_of_another_user_fails(
    as_user, admin_user, regular_user, user_factory
):
    other = await user_factory(email="other@example.com")
    c = as_user(admin_user)
    r = await c.patch(f"{BASE}/{regular_user.id}", json={"email": other.email})
    assert r.status_code == 400
    assert r.json()["type"] == "user_already_exists"


async def test_patch_with_email_of_deleted_user_fails(
    as_user, admin_user, regular_user, deleted_user_factory
):
    deleted = await deleted_user_factory()
    c = as_user(admin_user)
    r = await c.patch(f"{BASE}/{regular_user.id}", json={"email": deleted.email})
    assert r.status_code == 400


async def test_patch_with_own_email_is_allowed(as_user, admin_user, regular_user):
    c = as_user(admin_user)
    r = await c.patch(
        f"{BASE}/{regular_user.id}", json={"email": regular_user.email, "name": "Same"}
    )
    assert r.status_code == 200, r.text


async def test_patch_unknown_user_returns_404(as_user, admin_user):
    c = as_user(admin_user)
    r = await c.patch(f"{BASE}/{uuid.uuid4()}", json={"name": "X"})
    assert r.status_code == 404


async def test_patch_deleted_user_returns_404(
    as_user, admin_user, deleted_user_factory
):
    deleted = await deleted_user_factory()
    c = as_user(admin_user)
    r = await c.patch(f"{BASE}/{deleted.id}", json={"name": "X"})
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


async def test_admin_can_soft_delete_user(as_user, admin_user, regular_user):
    c = as_user(admin_user)

    r = await c.delete(f"{BASE}/{regular_user.id}")
    assert r.status_code == 204

    r = await c.get(f"{BASE}/{regular_user.id}")
    assert r.status_code == 200
    assert r.json()["deleted_at"] is not None


async def test_delete_already_deleted_user_returns_400(
    as_user, admin_user, deleted_user_factory
):
    deleted = await deleted_user_factory()
    c = as_user(admin_user)
    r = await c.delete(f"{BASE}/{deleted.id}")
    assert r.status_code == 400
    assert r.json()["type"] == "user_already_deleted"


async def test_delete_unknown_user_returns_404(as_user, admin_user):
    c = as_user(admin_user)
    r = await c.delete(f"{BASE}/{uuid.uuid4()}")
    assert r.status_code == 404
