import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.challenges.models.challenge_participant import ChallengeParticipant


async def get_challenge_ranking(
    session: AsyncSession, challenge_id: uuid.UUID
) -> list[ChallengeParticipant]:
    results = await session.scalars(
        select(ChallengeParticipant)
        .where(
            ChallengeParticipant.challenge_id == challenge_id,
            ChallengeParticipant.deleted_at.is_(None),
        )
        .options(
            selectinload(ChallengeParticipant.user),
            selectinload(ChallengeParticipant.semana_participant),
        )
        .order_by(desc(ChallengeParticipant.score))
        .limit(10)
    )

    return list(results.all())


async def get_challenge_participant_by_id(
    session: AsyncSession, participant_id: uuid.UUID
) -> ChallengeParticipant | None:
    result = await session.execute(
        select(ChallengeParticipant)
        .where(
            ChallengeParticipant.id == participant_id,
            ChallengeParticipant.deleted_at.is_(None),
        )
        .options(
            selectinload(ChallengeParticipant.user),
            selectinload(ChallengeParticipant.semana_participant),
        )
    )
    return result.scalar_one_or_none()


async def get_challenge_participant(
    session: AsyncSession,
    user_id: uuid.UUID,
    challenge_id: uuid.UUID,
    for_update: bool = False,
) -> ChallengeParticipant | None:

    command = (
        select(ChallengeParticipant)
        .where(
            ChallengeParticipant.user_id == user_id,
            ChallengeParticipant.challenge_id == challenge_id,
            ChallengeParticipant.deleted_at.is_(None),
        )
        .options(
            selectinload(ChallengeParticipant.user),
            selectinload(ChallengeParticipant.semana_participant),
        )
    )

    if for_update:
        command = command.with_for_update()

    result = await session.execute(command)
    return result.scalar_one_or_none()


async def list_challenge_participants(
    session: AsyncSession,
    challenge_id: uuid.UUID | None = None,
) -> list[ChallengeParticipant]:
    query = select(ChallengeParticipant).where(
        ChallengeParticipant.deleted_at.is_(None)
    )

    if challenge_id is not None:
        query = query.where(ChallengeParticipant.challenge_id == challenge_id)

    query = query.order_by(
        ChallengeParticipant.score.desc(),
        ChallengeParticipant.created_at.desc(),
    )

    result = await session.execute(query)
    return list(result.scalars().all())


async def create_challenge_participant(
    session: AsyncSession,
    user_id: uuid.UUID,
    challenge_id: uuid.UUID,
    score: int = 0,
    semana_participant_id: uuid.UUID | None = None,
) -> ChallengeParticipant:
    participant = ChallengeParticipant(
        user_id=user_id,
        challenge_id=challenge_id,
        score=score,
        semana_participant_id=semana_participant_id,
    )
    session.add(participant)
    await session.flush()
    return participant


async def update_challenge_participant(
    session: AsyncSession,
    participant: ChallengeParticipant,
    score: int | None = None,
) -> ChallengeParticipant:
    if score is not None:
        participant.score = score

    await session.flush()
    return participant


async def add_challenge_participant_score(
    session: AsyncSession,
    challenge_id: uuid.UUID,
    participant_id: uuid.UUID,
    amount: int,
) -> ChallengeParticipant | None:
    participant = await session.scalar(
        select(ChallengeParticipant)
        .where(
            ChallengeParticipant.id == participant_id,
            ChallengeParticipant.challenge_id == challenge_id,
            ChallengeParticipant.deleted_at.is_(None),
        )
        .options(selectinload(ChallengeParticipant.semana_participant))
        .with_for_update()
    )
    if participant is None:
        return None

    participant.score += amount
    await session.flush()
    return participant


# evitando muita dor de cabeça,
# o challenge_participant pode ficar com hard delete por enquanto
async def delete_challenge_participant(
    session: AsyncSession, participant: ChallengeParticipant
) -> ChallengeParticipant:

    await session.delete(participant)
    await session.flush()
    return participant
