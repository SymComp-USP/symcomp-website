"""Testes que expõem os bugs de soft-delete restantes."""

from __future__ import annotations

from datetime import UTC, datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.challenges.models.answer import Answer
from app.challenges.models.challenge_participant import ChallengeParticipant


async def test_deleted_answer_does_not_appear_in_get_challenge(
    client: AsyncClient,
    as_user,
    user,
    challenge,
    questions,
    db_session: AsyncSession,
):
    c = as_user(user)
    await c.post(f"api/v1/challenge/{challenge.id}/join")

    p = await db_session.scalar(
        __import__("sqlalchemy")
        .select(ChallengeParticipant)
        .where(
            ChallengeParticipant.user_id == user.id,
            ChallengeParticipant.challenge_id == challenge.id,
        )
    )

    db_session.add(
        Answer(
            participant_id=p.id,
            question_id=questions[0].id,
            content="4",
            is_correct=True,
            deleted_at=datetime.now(UTC),
        )
    )
    await db_session.flush()

    r = await c.get(f"api/v1/challenge/{challenge.id}")
    data = r.json()
    q0 = next(q for q in data["questions"] if q["id"] == str(questions[0].id))
    assert q0["current_answer"] is None, "resposta soft-deletada ainda aparece"


async def test_deleted_answer_not_counted_on_submit(
    client: AsyncClient,
    as_user,
    user,
    challenge,
    questions,
    db_session: AsyncSession,
):
    c = as_user(user)
    await c.post(f"api/v1/challenge/{challenge.id}/join")

    import sqlalchemy

    p = await db_session.scalar(
        sqlalchemy.select(ChallengeParticipant).where(
            ChallengeParticipant.user_id == user.id,
            ChallengeParticipant.challenge_id == challenge.id,
        )
    )

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

    r = await c.post(f"api/v1/challenge/{challenge.id}/submit")
    assert r.json()["score"] == 75, "resposta deletada somou pontos"
