import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.atividade.models import Atividade, Presenca, StatusAtividade
from app.core.exceptions.app_errors import BadRequestError
from app.semana.models import PointEvent, Semana, SemanaParticipant
from app.semana.services import add_points, get_or_create_participant
from app.users.models import User
from app.users.services import get_user_by_email


async def list_atividades(session: AsyncSession, semana_id: int) -> list[Atividade]:
    result = await session.scalars(
        select(Atividade)
        .where(Atividade.semana_id == semana_id)
        .order_by(Atividade.comeca_as)
    )
    return list(result.all())


async def get_atividade(
    session: AsyncSession, semana_id: int, atividade_id: UUID
) -> Atividade | None:
    return await session.scalar(
        select(Atividade).where(
            Atividade.id == atividade_id, Atividade.semana_id == semana_id
        )
    )


async def get_atividade_by_codigo(
    session: AsyncSession, semana_id: int, codigo: str
) -> Atividade | None:
    return await session.scalar(
        select(Atividade).where(
            Atividade.semana_id == semana_id, Atividade.codigo == codigo
        )
    )


def _new_codigo() -> str:
    return f"{secrets.randbelow(10_000):04d}"


async def _unique_codigo(
    session: AsyncSession, semana_id: int, exclude_id: UUID | None = None
) -> str:
    for _ in range(10_000):
        codigo = _new_codigo()
        exists = await session.scalar(
            select(Atividade.id).where(
                Atividade.semana_id == semana_id,
                Atividade.codigo == codigo,
                Atividade.id != exclude_id if exclude_id else True,
            )
        )
        if exists is None:
            return codigo
    raise BadRequestError("No activity code is available for this Semana.")


async def create_atividade(
    session: AsyncSession, semana: Semana, **fields
) -> Atividade:
    atividade = Atividade(
        semana_id=semana.id,
        codigo=await _unique_codigo(session, semana.id),
        **fields,
    )
    session.add(atividade)
    await session.flush()
    return atividade


async def regenerate_codigo(session: AsyncSession, atividade: Atividade) -> Atividade:
    atividade.codigo = await _unique_codigo(session, atividade.semana_id, atividade.id)
    await session.flush()
    return atividade


async def list_presencas(session: AsyncSession, atividade_id: UUID) -> list[Presenca]:
    result = await session.scalars(
        select(Presenca)
        .where(Presenca.atividade_id == atividade_id)
        .order_by(Presenca.created_at.desc())
    )
    return list(result.all())


async def register_manual_presence(
    session: AsyncSession, atividade: Atividade, nome: str, email: str
) -> Presenca:
    email = email.strip().lower()
    existing = await session.scalar(
        select(Presenca).where(
            Presenca.atividade_id == atividade.id, Presenca.email == email
        )
    )
    if existing is not None:
        return existing

    user = await get_user_by_email(session, email)
    presence = Presenca(
        atividade_id=atividade.id,
        user_id=user.id if user else None,
        nome=nome.strip(),
        email=email,
        horas=atividade.horas,
    )
    session.add(presence)
    await session.flush()

    if user is not None and atividade.pontos:
        participant = await get_or_create_participant(
            session, await session.get(Semana, atividade.semana_id), user
        )
        await add_points(
            session,
            participant,
            atividade.pontos,
            source_type="atividade",
            source_id=atividade.id,
            reason=atividade.titulo or "Atividade",
        )
    return presence


async def delete_presence(session: AsyncSession, presence: Presenca) -> None:
    if presence.user_id is not None:
        point_event = await session.scalar(
            select(PointEvent).where(
                PointEvent.semana_participant_id.in_(
                    select(SemanaParticipant.id).where(
                        SemanaParticipant.user_id == presence.user_id,
                        SemanaParticipant.semana_id == presence.atividade.semana_id,
                    )
                ),
                PointEvent.source_type == "atividade",
                PointEvent.source_id == presence.atividade_id,
            )
        )
        if point_event is not None:
            await session.delete(point_event)
    await session.delete(presence)


async def update_atividade(
    session: AsyncSession, atividade: Atividade, fields: dict
) -> Atividade:
    values = {key: value for key, value in fields.items() if value is not None}
    starts = values.get("comeca_as", atividade.comeca_as)
    ends = values.get("termina_as", atividade.termina_as)
    if ends <= starts:
        raise BadRequestError("termina_as must be after comeca_as")
    for key, value in values.items():
        setattr(atividade, key, value)
    await session.flush()
    return atividade


async def register_presence(
    session: AsyncSession,
    atividade: Atividade,
    user: User | None,
    nome: str | None,
    email: str | None,
) -> tuple[Presenca, int]:
    now = datetime.now(UTC)
    if atividade.status != StatusAtividade.CONFIRMADA:
        raise BadRequestError("Activity is not confirmed.")
    if now < atividade.comeca_as or now > atividade.termina_as + timedelta(minutes=30):
        raise BadRequestError("Attendance window is closed.")

    if user is not None:
        nome, email = user.name, user.email
    elif not nome or not email:
        raise BadRequestError("nome and email are required for visitors.")

    email = email.strip().lower()
    existing = await session.scalar(
        select(Presenca).where(
            Presenca.atividade_id == atividade.id,
            Presenca.email == email,
        )
    )
    if existing is not None:
        return existing, 0

    presence = Presenca(
        atividade_id=atividade.id,
        user_id=user.id if user else None,
        nome=nome.strip(),
        email=email,
        horas=atividade.horas,
    )
    session.add(presence)
    await session.flush()

    points = 0
    if user is not None:
        participant = await get_or_create_participant(
            session, await session.get(Semana, atividade.semana_id), user
        )
        if atividade.pontos:
            await add_points(
                session,
                participant,
                atividade.pontos,
                source_type="atividade",
                source_id=atividade.id,
                reason=atividade.titulo or "Atividade",
            )
            points = atividade.pontos
    return presence, points
