"""Testes de soft delete de challenge."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.challenges import exceptions as challenge_exceptions
from app.challenges.services import challenge as challenge_service


async def test_soft_delete_sets_deleted_at(db_session: AsyncSession, challenge):
    await challenge_service.delete_challenge(db_session, challenge)

    assert challenge.deleted_at is not None
    assert await challenge_service.get_challenge_by_id(db_session, challenge.id) is None


async def test_delete_twice_raises(db_session: AsyncSession, challenge):
    await challenge_service.delete_challenge(db_session, challenge)
    with pytest.raises(challenge_exceptions.AlreadyDeletedError):
        await challenge_service.delete_challenge(db_session, challenge)
