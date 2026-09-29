"""Testes de `process_submission`."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.challenges.models.answer import Answer
from app.challenges.models.challenge_participant import ChallengeParticipant
from app.challenges.services import challenge as challenge_service


async def _make_participant(
    session: AsyncSession, user_id: uuid.UUID, challenge_id: uuid.UUID
) -> ChallengeParticipant:
    p = ChallengeParticipant(user_id=user_id, challenge_id=challenge_id)
    session.add(p)
    await session.flush()
    return p


async def test_process_submission_sums_only_correct_answers(
    db_session: AsyncSession, user, challenge, questions
):
    participant = await _make_participant(db_session, user.id, challenge.id)

    # Duas corretas, uma errada
    db_session.add_all(
        [
            Answer(
                participant_id=participant.id,
                question_id=questions[0].id,
                content="4",
                is_correct=True,
            ),
            Answer(
                participant_id=participant.id,
                question_id=questions[1].id,
                content="9",
                is_correct=True,
            ),
            Answer(
                participant_id=participant.id,
                question_id=questions[2].id,
                content="Rio",
                is_correct=False,
            ),
        ]
    )
    await db_session.flush()

    score = await challenge_service.process_submission(db_session, participant)

    assert score == 150  # 100 + 50
    assert participant.score == 150
    assert participant.submitted_at is not None


async def test_process_submission_ignores_deleted_answers(
    db_session: AsyncSession, user, challenge, questions
):
    from datetime import UTC, datetime

    participant = await _make_participant(db_session, user.id, challenge.id)

    correct = Answer(
        participant_id=participant.id,
        question_id=questions[0].id,
        content="4",
        is_correct=True,
    )
    deleted_correct = Answer(
        participant_id=participant.id,
        question_id=questions[1].id,
        content="9",
        is_correct=True,
        deleted_at=datetime.now(UTC),
    )
    db_session.add_all([correct, deleted_correct])
    await db_session.flush()

    score = await challenge_service.process_submission(db_session, participant)

    assert score == 100


async def test_process_submission_zero_when_no_answers(
    db_session: AsyncSession, user, challenge
):
    participant = await _make_participant(db_session, user.id, challenge.id)
    score = await challenge_service.process_submission(db_session, participant)
    assert score == 0
    assert participant.score == 0
