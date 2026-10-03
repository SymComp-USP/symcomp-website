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


def ensure_challenge_started(starts_at: datetime) -> None:
    if starts_at > datetime.now(UTC):
        raise challenge_exceptions.ChallengeNotStartedError()


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
        .where(Challenge.starts_at <= datetime.now(UTC))
        .options(selectinload(Challenge.questions), selectinload(Challenge.input))
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
    session: AsyncSession, participant: ChallengeParticipant, challenge: Challenge
) -> int:
    """Scores correct quiz answers proportionally against the challenge total."""

    correct_count = await session.scalar(
        select(func.count(Answer.id))
        .join(Question, Question.id == Answer.question_id)
        .where(
            Answer.participant_id == participant.id,
            Answer.deleted_at.is_(None),
            Answer.is_correct.is_(True),
        )
    )

    question_count = await session.scalar(
        select(func.count(Question.id)).where(Question.challenge_id == challenge.id)
    )
    score = (
        challenge.points_value * (correct_count or 0) // (question_count or 1)
        if question_count
        else 0
    )

    is_complete = bool(question_count) and (correct_count or 0) == question_count
    participant.submitted_at = datetime.now(UTC) if is_complete else None
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
        .options(selectinload(Challenge.questions), selectinload(Challenge.input))
    )
    return result.scalar_one_or_none()


async def list_challenges_paginated(
    session: AsyncSession,
    pagination: PaginationParams,
) -> Page[challenge_schemas.ChallengePublicResponse]:  # ← tipo correto
    conditions = (
        Challenge.deleted_at.is_(None),
        Challenge.starts_at <= datetime.now(UTC),
    )
    total = await session.scalar(select(func.count(Challenge.id)).where(*conditions))

    rows = (
        await session.scalars(
            select(Challenge)
            .where(*conditions)
            .options(selectinload(Challenge.input))
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
            .options(selectinload(Challenge.questions), selectinload(Challenge.input))
            .order_by(Challenge.created_at.desc(), Challenge.id)
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
    ).all()
    return Page[challenge_schemas.AdminChallengeResponse](
        items=[
            challenge_schemas.AdminChallengeResponse.model_validate(c) for c in rows
        ],
        total=total or 0,
        limit=pagination.limit,
        offset=pagination.offset,
    )


async def create_challenge(
    session: AsyncSession,
    title: str,
    description: str = "",
    scoring_type: ChallengeScoringType = ChallengeScoringType.QUIZ,
    starts_at: datetime | None = None,
    finishes_at: datetime | None = None,
    semana_id: int | None = None,
    points_value: int = 0,
    resource_urls: list[str] | None = None,
) -> Challenge:
    challenge = Challenge(
        title=title,
        description=description,
        points_value=points_value,
        scoring_type=scoring_type,
        semana_id=semana_id,
        resource_urls=resource_urls or [],
    )
    if finishes_at is not None:
        challenge.finishes_at = finishes_at
    if starts_at is not None:
        challenge.starts_at = starts_at
    session.add(challenge)
    await session.flush()
    return challenge


async def update_challenge(
    session: AsyncSession,
    challenge: Challenge,
    *,
    title: str | None = None,
    description: str | None = None,
    scoring_type: ChallengeScoringType | None = None,
    starts_at: datetime | None = None,
    finishes_at: datetime | None = None,
    semana_id: int | None = None,
    points_value: int | None = None,
    resource_urls: list[str] | None = None,
) -> Challenge:
    if title is not None:
        challenge.title = title
    if description is not None:
        challenge.description = description
    if scoring_type is not None:
        challenge.scoring_type = scoring_type
    if points_value is not None:
        challenge.points_value = points_value
    if finishes_at is not None:
        challenge.finishes_at = finishes_at
    if starts_at is not None:
        challenge.starts_at = starts_at
    if semana_id is not None:
        challenge.semana_id = semana_id
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
