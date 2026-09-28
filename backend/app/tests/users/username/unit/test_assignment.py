"""Testes de `assign_username`."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.app_errors import NotFoundError
from app.users.exceptions import NoAvailableUsername
from app.users.username import services as username_service


async def test_assigns_first_available_username(
    db_session: AsyncSession, user_factory, username_catalog
):
    user = await user_factory(email="username-first@example.com")
    username = await username_service.assign_username(user.id, db_session)

    assert username.nickname in {
        catalog_username.nickname for catalog_username in username_catalog
    }
    assert user.username_id == username.id


async def test_returns_existing_username_if_already_assigned(
    db_session: AsyncSession, user_factory, username_catalog
):
    user = await user_factory(email="username-existing@example.com")
    user.username_id = username_catalog[0].id
    await db_session.flush()

    username = await username_service.assign_username(user.id, db_session)

    assert username.id == username_catalog[0].id


async def test_username_cannot_be_assigned_to_multiple_users(
    db_session: AsyncSession, user_factory, username_catalog
):
    user = await user_factory(email="username-owner@example.com")
    other_user = await user_factory(email="username-other@example.com")
    user.username_id = username_catalog[0].id
    await db_session.flush()

    with pytest.raises(IntegrityError):
        async with db_session.begin_nested():
            other_user.username_id = username_catalog[0].id
            await db_session.flush()


async def test_raises_when_no_username_available(
    db_session: AsyncSession, username_catalog
):
    import uuid

    from app.users.models import User

    user = User(
        id=uuid.uuid4(),
        email="username-catalog-exhausted@example.com",
        name="Catalog Exhausted",
        password_hash="x",
    )
    db_session.add(user)
    await db_session.flush()

    # Assigns every catalog entry to a different user.
    for i, u in enumerate(username_catalog):
        dummy = User(
            id=uuid.uuid4(),
            email=f"dummy-{i}@t.local",
            name=f"Dummy {i}",
            password_hash="x",
            is_verified=True,
        )
        db_session.add(dummy)
        await db_session.flush()
        dummy.username_id = u.id
    await db_session.flush()

    with pytest.raises(NoAvailableUsername):
        await username_service.assign_username(user.id, db_session)


async def test_raises_when_user_does_not_exist(
    db_session: AsyncSession, username_catalog
):
    import uuid

    with pytest.raises(NotFoundError):
        await username_service.assign_username(uuid.uuid4(), db_session)
