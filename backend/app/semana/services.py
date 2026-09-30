from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.semana.models import PointEvent, Semana, SemanaParticipant
from app.semana.nicknames import generate_nickname
from app.users.models import User


async def get_semana(session: AsyncSession, semana_id: int) -> Semana | None:
    return await session.get(Semana, semana_id)


async def list_semanas(
    session: AsyncSession, *, include_admin_relations: bool = False
) -> list[Semana]:
    statement = select(Semana).order_by(Semana.ano.desc())
    if include_admin_relations:
        statement = statement.options(
            selectinload(Semana.challenges),
            selectinload(Semana.participants),
        )
    return list((await session.scalars(statement)).all())


async def create_semana(session: AsyncSession, nome: str, ano: int) -> Semana:
    semana = Semana(nome=nome, ano=ano)
    session.add(semana)
    await session.flush()
    return semana


async def update_semana(
    session: AsyncSession,
    semana: Semana,
    *,
    nome: str | None = None,
    ano: int | None = None,
) -> Semana:
    if nome is not None:
        semana.nome = nome
    if ano is not None:
        semana.ano = ano
    await session.flush()
    return semana


async def get_or_create_participant(
    session: AsyncSession, semana: Semana, user: User
) -> SemanaParticipant:
    participant = await session.scalar(
        select(SemanaParticipant).where(
            SemanaParticipant.semana_id == semana.id,
            SemanaParticipant.user_id == user.id,
        )
    )
    if participant is not None:
        if participant.nickname is None:
            participant.nickname = await generate_nickname(session, semana.id)
            await session.flush()
        return participant

    participant = SemanaParticipant(
        semana_id=semana.id,
        user_id=user.id,
        nickname=await generate_nickname(session, semana.id),
    )
    session.add(participant)
    await session.flush()
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
            SemanaParticipant.nickname,
            func.coalesce(func.sum(PointEvent.amount), 0).label("points"),
        )
        .outerjoin(PointEvent)
        .where(SemanaParticipant.semana_id == semana_id)
        .group_by(
            SemanaParticipant.id,
            SemanaParticipant.nickname,
        )
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
