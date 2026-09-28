"""Testes de `get_challenge_with_context`."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.challenges.models.answer import Answer
from app.challenges.models.challenge_participant import ChallengeParticipant
from app.challenges.services import challenge as challenge_service
from app.core.exceptions.app_errors import NotFoundError


async def test_returns_challenge_questions_and_no_participant(
    db_session: AsyncSession, user, challenge, questions
):
    (
        c,
        qs,
        answers_by_qid,
        participant,
    ) = await challenge_service.get_challenge_with_context(
        db_session, challenge.id, user.id
    )
    assert c.id == challenge.id
    assert len(qs) == len(questions)
    assert answers_by_qid == {}
    assert participant is None


async def test_includes_saved_answers_for_participant(
    db_session: AsyncSession, user, challenge, questions
):
    p = ChallengeParticipant(user_id=user.id, challenge_id=challenge.id)
    db_session.add(p)
    await db_session.flush()

    db_session.add(
        Answer(
            participant_id=p.id,
            question_id=questions[0].id,
            content="4",
            is_correct=True,
        )
    )
    await db_session.flush()

    (
        _,
        _,
        answers_by_qid,
        participant,
    ) = await challenge_service.get_challenge_with_context(
        db_session, challenge.id, user.id
    )
    assert participant is not None
    assert answers_by_qid == {questions[0].id: "4"}


async def test_ignores_soft_deleted_answers(
    db_session: AsyncSession, user, challenge, questions
):
    p = ChallengeParticipant(user_id=user.id, challenge_id=challenge.id)
    db_session.add(p)
    await db_session.flush()

    db_session.add_all(
        [
            Answer(
                participant_id=p.id,
                question_id=questions[0].id,
                content="4",
                is_correct=True,
            ),
            Answer(
                participant_id=p.id,
                question_id=questions[1].id,
                content="9",
                is_correct=True,
                deleted_at=datetime.now(UTC),
            ),
        ]
    )
    await db_session.flush()

    _, _, answers_by_qid, _ = await challenge_service.get_challenge_with_context(
        db_session, challenge.id, user.id
    )

    assert answers_by_qid == {questions[0].id: "4"}  # sem a deletada


async def test_raises_when_challenge_not_found(db_session: AsyncSession, user):
    import uuid

    with pytest.raises(NotFoundError):
        await challenge_service.get_challenge_with_context(
            db_session, uuid.uuid4(), user.id
        )
