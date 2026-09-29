"""Testes de `assign_username` por Semana."""

from __future__ import annotations

import uuid

import pytest
from app.core.exceptions.app_errors import NotFoundError
from app.semana.models import SemanaEvent, SemanaParticipant
from app.users.exceptions import NoAvailableUsername
from app.users.username import services as username_service
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def _participant(db_session, user_factory, *, semana_id, email):
    user = await user_factory(email=email)
    participant = SemanaParticipant(user_id=user.id, semana_id=semana_id)
    db_session.add(participant)
    await db_session.flush()
    return participant


async def test_assigns_first_available_username(
    db_session: AsyncSession, user_factory, username_catalog
):
    semana = SemanaEvent(nome="Semana", ano=2026)
    db_session.add(semana)
    await db_session.flush()
    participant = await _participant(
        db_session, user_factory, semana_id=semana.id, email="username-first@example.com"
    )

    username = await username_service.assign_username(participant.id, db_session)

    assert username.nickname in {item.nickname for item in username_catalog}
    assert participant.username_id == username.id


async def test_returns_existing_username_if_already_assigned(
    db_session: AsyncSession, user_factory, username_catalog
):
    semana = SemanaEvent(nome="Semana", ano=2026)
    db_session.add(semana)
    await db_session.flush()
    participant = await _participant(
        db_session,
        user_factory,
        semana_id=semana.id,
        email="username-existing@example.com",
    )
    participant.username_id = username_catalog[0].id
    await db_session.flush()

    username = await username_service.assign_username(participant.id, db_session)

    assert username.id == username_catalog[0].id


async def test_username_cannot_be_assigned_twice_in_same_semana(
    db_session: AsyncSession, user_factory, username_catalog
):
    semana = SemanaEvent(nome="Semana", ano=2026)
    db_session.add(semana)
    await db_session.flush()
    first = await _participant(
        db_session, user_factory, semana_id=semana.id, email="username-owner@example.com"
    )
    other = await _participant(
        db_session, user_factory, semana_id=semana.id, email="username-other@example.com"
    )
    first.username_id = username_catalog[0].id
    await db_session.flush()

    with pytest.raises(IntegrityError):
        async with db_session.begin_nested():
            other.username_id = username_catalog[0].id
            await db_session.flush()


async def test_same_username_can_be_used_in_different_semanas(
    db_session: AsyncSession, user_factory, username_catalog
):
    first_semana = SemanaEvent(nome="Semana 1", ano=2026)
    second_semana = SemanaEvent(nome="Semana 2", ano=2027)
    db_session.add_all([first_semana, second_semana])
    await db_session.flush()
    first = await _participant(
        db_session, user_factory, semana_id=first_semana.id, email="one@example.com"
    )
    second = await _participant(
        db_session, user_factory, semana_id=second_semana.id, email="two@example.com"
    )
    first.username_id = username_catalog[0].id
    second.username_id = username_catalog[0].id

    await db_session.flush()


async def test_raises_when_no_username_available(
    db_session: AsyncSession, user_factory, username_catalog
):
    semana = SemanaEvent(nome="Semana", ano=2026)
    db_session.add(semana)
    await db_session.flush()
    participants = [
        await _participant(
            db_session,
            user_factory,
            semana_id=semana.id,
            email=f"username-{i}@example.com",
        )
        for i in range(len(username_catalog) + 1)
    ]
    for participant, username in zip(participants, username_catalog):
        participant.username_id = username.id
    await db_session.flush()

    with pytest.raises(NoAvailableUsername):
        await username_service.assign_username(participants[-1].id, db_session)


async def test_raises_when_participant_does_not_exist(
    db_session: AsyncSession, username_catalog
):
    with pytest.raises(NotFoundError):
        await username_service.assign_username(uuid.uuid4(), db_session)
