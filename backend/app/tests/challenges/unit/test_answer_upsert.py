"""Testes de `upsert_answer`."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.challenges.models.challenge_participant import ChallengeParticipant
from app.challenges.services import answer as answer_service
from app.core.exceptions.app_errors import NotFoundError


async def _make_participant(session: AsyncSession, user_id, challenge_id):
    p = ChallengeParticipant(user_id=user_id, challenge_id=challenge_id)
    session.add(p)
    await session.flush()
    return p


async def test_upsert_inserts_when_new(
    db_session: AsyncSession, user, challenge, questions
):
    participant = await _make_participant(db_session, user.id, challenge.id)

    answer = await answer_service.upsert_answer(
        db_session, participant.id, questions[0].id, "4"
    )

    assert answer.content == "4"
    assert answer.is_correct is True


async def test_upsert_updates_content_and_is_correct(
    db_session: AsyncSession, user, challenge, questions
):
    """Garante que is_correct é recalculado no update — o bug clássico do ON CONFLICT."""
    participant = await _make_participant(db_session, user.id, challenge.id)

    # Primeira: errado
    await answer_service.upsert_answer(db_session, participant.id, questions[0].id, "5")

    # Depois: certo
    answer = await answer_service.upsert_answer(
        db_session, participant.id, questions[0].id, "4"
    )

    assert answer.content == "4"
    assert answer.is_correct is True, "is_correct não foi recalculado no update"


async def test_upsert_normalizes_case_and_whitespace(
    db_session: AsyncSession, user, challenge, questions
):
    participant = await _make_participant(db_session, user.id, challenge.id)

    answer = await answer_service.upsert_answer(
        db_session, participant.id, questions[2].id, "  brasília  "
    )

    assert answer.is_correct is True


async def test_upsert_rejects_question_from_other_challenge(
    db_session: AsyncSession, user, challenge, manual_challenge
):
    """Pergunta não pertence ao challenge do participante → NotFoundError."""
    from app.challenges.models.question import Question

    foreign_q = Question(
        prompt="?", answer="?", points_value=10, challenge_id=manual_challenge.id
    )
    db_session.add(foreign_q)
    await db_session.flush()

    participant = await _make_participant(db_session, user.id, challenge.id)

    with pytest.raises(NotFoundError):
        await answer_service.upsert_answer(
            db_session, participant.id, foreign_q.id, "x"
        )


async def test_upsert_rejects_nonexistent_question(
    db_session: AsyncSession, user, challenge
):
    import uuid

    participant = await _make_participant(db_session, user.id, challenge.id)

    with pytest.raises(NotFoundError):
        await answer_service.upsert_answer(
            db_session, participant.id, uuid.uuid4(), "x"
        )


async def test_upsert_reactivates_soft_deleted_answer(
    db_session: AsyncSession, user, challenge, questions
):
    from datetime import UTC, datetime

    participant = await _make_participant(db_session, user.id, challenge.id)

    answer = await answer_service.upsert_answer(
        db_session, participant.id, questions[0].id, "4"
    )
    answer.deleted_at = datetime.now(UTC)
    await db_session.flush()

    reactivated = await answer_service.upsert_answer(
        db_session, participant.id, questions[0].id, "4"
    )

    assert reactivated.deleted_at is None
