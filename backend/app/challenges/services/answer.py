import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.challenges import exceptions as challenge_exceptions
from app.challenges.models.answer import Answer
from app.challenges.models.challenge import Challenge
from app.challenges.models.challenge_participant import ChallengeParticipant
from app.challenges.models.question import Question
from app.challenges.services import challenge as challenge_service
from app.core.exceptions.app_errors import NotFoundError


async def get_answer_by_id(
    session: AsyncSession, answer_id: uuid.UUID
) -> Answer | None:
    result = await session.execute(
        select(Answer).where(Answer.id == answer_id, Answer.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def list_answers(
    session: AsyncSession,
    participant_id: uuid.UUID | None = None,
    question_id: uuid.UUID | None = None,
) -> list[Answer]:
    query = select(Answer).where(Answer.deleted_at.is_(None))

    if participant_id is not None:
        query = query.where(Answer.participant_id == participant_id)
    if question_id is not None:
        query = query.where(Answer.question_id == question_id)

    result = await session.execute(query)
    return list(result.scalars().all())


async def upsert_answer(
    session: AsyncSession,
    participant_id: uuid.UUID,
    question_id: uuid.UUID,
    content: str,
) -> Answer:

    result = await session.execute(
        select(Question, Challenge.finishes_at)
        .join(Challenge, Challenge.id == Question.challenge_id)
        .join(ChallengeParticipant, ChallengeParticipant.challenge_id == Challenge.id)
        .where(
            Question.id == question_id,
            Challenge.deleted_at.is_(None),
            ChallengeParticipant.id == participant_id,
            ChallengeParticipant.deleted_at.is_(None),
        )
    )

    question_and_deadline = result.one_or_none()
    if question_and_deadline is None:
        raise NotFoundError("Could not find question with given ID.")

    question, finishes_at = question_and_deadline
    challenge_service.ensure_challenge_open(finishes_at)

    is_correct = content.strip().lower() == question.answer.strip().lower()

    stmt = (
        insert(Answer)
        .values(
            participant_id=participant_id,
            question_id=question_id,
            content=content,
            is_correct=is_correct,
        )
        .on_conflict_do_update(
            constraint="uq_participant_question",
            set_={"content": content, "is_correct": is_correct, "deleted_at": None},
        )
        .returning(Answer)
        .execution_options(populate_existing=True)
    )

    result = await session.execute(stmt)
    return result.scalar_one()


async def delete_answer(session: AsyncSession, answer_record: Answer) -> Answer:
    if answer_record.deleted_at is not None:
        raise challenge_exceptions.AlreadyDeletedError()

    answer_record.deleted_at = datetime.now(UTC)
    await session.flush()
    return answer_record
