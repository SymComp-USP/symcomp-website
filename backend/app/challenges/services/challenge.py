import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.challenges import exceptions as challenge_exceptions
from app.challenges import schemas as challenge_schemas
from app.challenges.models.answer import Answer
from app.challenges.models.challenge import Challenge, ChallengeScoringType
from app.challenges.models.challenge_participant import ChallengeParticipant
from app.challenges.models.question import Question
from app.core.exceptions.app_errors import NotFoundError
from app.core.pagination import Page, PaginationParams


def ensure_challenge_open(finishes_at: datetime) -> None:
    if finishes_at <= datetime.now(UTC):
        raise challenge_exceptions.ChallengeClosedError()


async def get_challenge_with_context(
    session: AsyncSession,
    challenge_id: uuid.UUID,
    user_id: uuid.UUID,
) -> tuple[
    Challenge, list[Question], dict[uuid.UUID, str], ChallengeParticipant | None
]:
    """Carrega o challenge, suas questões, e (se o usuário for participante)
    as respostas já salvas + o participante."""

    challenge = await session.scalar(
        select(Challenge)
        .where(Challenge.id == challenge_id)
        .where(Challenge.deleted_at.is_(None))
        .options(selectinload(Challenge.questions))
    )

    if challenge is None:
        raise NotFoundError("Challenge not found.")

    participant = await session.scalar(
        select(ChallengeParticipant).where(
            ChallengeParticipant.user_id == user_id,
            ChallengeParticipant.challenge_id == challenge_id,
        )
    )

    current_answers_by_qid: dict[uuid.UUID, str] = {}
    if participant is not None:
        rows = (
            await session.execute(
                select(Answer.question_id, Answer.content).where(
                    Answer.participant_id == participant.id, Answer.deleted_at.is_(None)
                )
            )
        ).all()
        current_answers_by_qid = dict(rows)

    return challenge, challenge.questions, current_answers_by_qid, participant


async def process_submission(
    session: AsyncSession, participant: ChallengeParticipant
) -> int:
    """Processa a pontuação das respostas de challenge que sea do tipo "quiz" """

    rows = (
        await session.execute(
            select(Answer.is_correct, Question.points_value)
            .join(Question, Question.id == Answer.question_id)
            .where(Answer.participant_id == participant.id, Answer.deleted_at.is_(None))
        )
    ).all()

    score = sum(row[1] for row in rows if row[0])

    participant.submitted_at = datetime.now(UTC)
    participant.score = score

    await session.flush()

    return score


async def get_challenge_by_id(
    session: AsyncSession, challenge_id: uuid.UUID
) -> Challenge | None:
    result = await session.execute(
        select(Challenge)
        .where(
            Challenge.id == challenge_id,
            Challenge.deleted_at.is_(None),
        )
        .options(selectinload(Challenge.questions))
    )
    return result.scalar_one_or_none()


async def list_challenges_paginated(
    session: AsyncSession,
    pagination: PaginationParams,
) -> Page[challenge_schemas.ChallengePublicResponse]:  # ← tipo correto
    total = await session.scalar(
        select(func.count(Challenge.id)).where(Challenge.deleted_at.is_(None))
    )

    rows = (
        await session.scalars(
            select(Challenge)
            .where(Challenge.deleted_at.is_(None))
            .order_by(Challenge.created_at.desc(), Challenge.id)
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
    ).all()

    return Page[challenge_schemas.ChallengePublicResponse](
        items=[
            challenge_schemas.ChallengePublicResponse.model_validate(c) for c in rows
        ],
        total=total or 0,
        limit=pagination.limit,
        offset=pagination.offset,
    )


async def list_admin_challenges_paginated(
    session: AsyncSession,
    pagination: PaginationParams,
) -> Page[challenge_schemas.AdminChallengeResponse]:
    total = await session.scalar(
        select(func.count(Challenge.id)).where(Challenge.deleted_at.is_(None))
    )
    rows = (
        await session.scalars(
            select(Challenge)
            .where(Challenge.deleted_at.is_(None))
            .options(selectinload(Challenge.questions))
            .order_by(Challenge.created_at.desc(), Challenge.id)
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
    ).all()
    return Page[challenge_schemas.AdminChallengeResponse](
        items=[challenge_schemas.AdminChallengeResponse.model_validate(c) for c in rows],
        total=total or 0,
        limit=pagination.limit,
        offset=pagination.offset,
    )


async def create_challenge(
    session: AsyncSession,
    title: str,
    scoring_type: ChallengeScoringType = ChallengeScoringType.QUIZ,
    finishes_at: datetime | None = None,
    prompt: str = "",
    semana_id: int | None = None,
    points_value: int = 0,
    input_answer: str | None = None,
    resource_urls: list[str] | None = None,
) -> Challenge:
    challenge = Challenge(
        title=title,
        prompt=prompt,
        scoring_type=scoring_type,
        semana_id=semana_id,
        points_value=points_value,
        input_answer=input_answer,
        resource_urls=resource_urls or [],
    )
    if finishes_at is not None:
        challenge.finishes_at = finishes_at
    session.add(challenge)
    await session.flush()
    return challenge


async def update_challenge(
    session: AsyncSession,
    challenge: Challenge,
    *,
    title: str | None = None,
    finishes_at: datetime | None = None,
    semana_id: int | None = None,
    prompt: str | None = None,
    points_value: int | None = None,
    input_answer: str | None = None,
    resource_urls: list[str] | None = None,
) -> Challenge:
    if title is not None:
        challenge.title = title
    if finishes_at is not None:
        challenge.finishes_at = finishes_at
    if semana_id is not None:
        challenge.semana_id = semana_id
    if prompt is not None:
        challenge.prompt = prompt
    if points_value is not None:
        challenge.points_value = points_value
    if input_answer is not None:
        challenge.input_answer = input_answer
    if resource_urls is not None:
        challenge.resource_urls = resource_urls

    await session.flush()
    return challenge


async def delete_challenge(session: AsyncSession, challenge: Challenge) -> Challenge:
    if challenge.deleted_at is not None:
        raise challenge_exceptions.AlreadyDeletedError()

    challenge.deleted_at = datetime.now(UTC)

    await session.flush()
    return challenge
