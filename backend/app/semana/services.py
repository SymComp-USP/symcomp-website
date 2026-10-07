from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.atividade.models import Atividade, Presenca
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
        .outerjoin(
            PointEvent,
            and_(
                PointEvent.semana_participant_id == SemanaParticipant.id,
                PointEvent.deleted_at.is_(None),
            ),
        )
        .where(SemanaParticipant.semana_id == semana_id)
        .group_by(
            SemanaParticipant.id,
            SemanaParticipant.nickname,
        )
        .order_by(func.coalesce(func.sum(PointEvent.amount), 0).desc())
    )
    return rows.all()


async def get_user_participation(session: AsyncSession, user_id):
    points_rows = await session.execute(
        select(
            Semana.id,
            Semana.nome,
            Semana.ano,
            SemanaParticipant.nickname,
            func.coalesce(func.sum(PointEvent.amount), 0).label("pontos"),
        )
        .join(SemanaParticipant, SemanaParticipant.semana_id == Semana.id)
        .outerjoin(PointEvent, PointEvent.semana_participant_id == SemanaParticipant.id)
        .where(
            SemanaParticipant.user_id == user_id,
            SemanaParticipant.deleted_at.is_(None),
            PointEvent.deleted_at.is_(None) | (PointEvent.id.is_(None)),
        )
        .group_by(
            Semana.id,
            Semana.nome,
            Semana.ano,
            SemanaParticipant.nickname,
        )
    )
    hours_rows = await session.execute(
        select(
            Atividade.semana_id,
            func.coalesce(func.sum(Presenca.horas), 0).label("horas"),
        )
        .join(Presenca, Presenca.atividade_id == Atividade.id)
        .where(
            Presenca.user_id == user_id,
            Presenca.deleted_at.is_(None),
            Atividade.deleted_at.is_(None),
        )
        .group_by(Atividade.semana_id)
    )
    points = {row.id: row for row in points_rows}
    hours = {row.semana_id: row.horas for row in hours_rows}
    semana_ids = set(points) | set(hours)
    weeks = []
    for semana_id in semana_ids:
        point_row = points.get(semana_id)
        weeks.append(
            {
                "semana_id": semana_id,
                "nome": point_row.nome
                if point_row
                else (await get_semana(session, semana_id)).nome,
                "ano": point_row.ano
                if point_row
                else (await get_semana(session, semana_id)).ano,
                "nickname": point_row.nickname if point_row else None,
                "pontos": int(point_row.pontos) if point_row else 0,
                "horas": int(hours.get(semana_id, 0)),
            }
        )
    weeks.sort(key=lambda week: week["ano"], reverse=True)
    return {
        "pontos": sum(week["pontos"] for week in weeks),
        "horas": sum(week["horas"] for week in weeks),
        "semanas": weeks,
    }


async def get_participant(
    session: AsyncSession, semana_id: int, participant_id
) -> SemanaParticipant | None:
    return await session.scalar(
        select(SemanaParticipant).where(
            SemanaParticipant.id == participant_id,
            SemanaParticipant.semana_id == semana_id,
        )
    )
