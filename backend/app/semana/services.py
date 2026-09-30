from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.semana.models import PointEvent, SemanaEvent, SemanaParticipant
from app.users.models import User
from app.users.username import services as username_services
from app.users.username.models import Username


async def get_semana(session: AsyncSession, semana_id: int) -> SemanaEvent | None:
    return await session.get(SemanaEvent, semana_id)


async def list_semanas(
    session: AsyncSession, *, include_admin_relations: bool = False
) -> list[SemanaEvent]:
    statement = select(SemanaEvent).order_by(SemanaEvent.ano.desc())
    if include_admin_relations:
        statement = statement.options(
            selectinload(SemanaEvent.challenges),
            selectinload(SemanaEvent.participants),
        )
    return list((await session.scalars(statement)).all())


async def create_semana(session: AsyncSession, nome: str, ano: int) -> SemanaEvent:
    semana = SemanaEvent(nome=nome, ano=ano)
    session.add(semana)
    await session.flush()
    return semana


async def update_semana(
    session: AsyncSession,
    semana: SemanaEvent,
    *,
    nome: str | None = None,
    ano: int | None = None,
) -> SemanaEvent:
    if nome is not None:
        semana.nome = nome
    if ano is not None:
        semana.ano = ano
    await session.flush()
    return semana


async def get_or_create_participant(
    session: AsyncSession, semana: SemanaEvent, user: User
) -> SemanaParticipant:
    participant = await session.scalar(
        select(SemanaParticipant)
        .where(
            SemanaParticipant.semana_id == semana.id,
            SemanaParticipant.user_id == user.id,
        )
        .options(selectinload(SemanaParticipant.username))
    )
    if participant is not None:
        if participant.username is None:
            await username_services.assign_username(participant.id, session)
        return participant

    participant = SemanaParticipant(
        semana_id=semana.id,
        user_id=user.id,
    )
    session.add(participant)
    await session.flush()
    await username_services.assign_username(participant.id, session)
    return participant


async def add_points(
    session: AsyncSession,
    participant: SemanaParticipant,
    amount: int,
    *,
    source_type: str,
    source_id=None,
    reason: str | None = None,
) -> PointEvent:
    event = PointEvent(
        semana_participant_id=participant.id,
        amount=amount,
        source_type=source_type,
        source_id=source_id,
        reason=reason,
    )
    session.add(event)
    await session.flush()
    return event


async def list_ranking(session: AsyncSession, semana_id: int):
    rows = await session.execute(
        select(
            SemanaParticipant.id,
            Username.nickname,
            func.coalesce(func.sum(PointEvent.amount), 0).label("points"),
        )
        .outerjoin(PointEvent)
        .join(Username, Username.id == SemanaParticipant.username_id)
        .where(SemanaParticipant.semana_id == semana_id)
        .group_by(SemanaParticipant.id, Username.nickname)
        .order_by(func.coalesce(func.sum(PointEvent.amount), 0).desc())
    )
    return rows.all()


async def get_participant(
    session: AsyncSession, semana_id: int, participant_id
) -> SemanaParticipant | None:
    return await session.scalar(
        select(SemanaParticipant).where(
            SemanaParticipant.id == participant_id,
            SemanaParticipant.semana_id == semana_id,
        )
    )
