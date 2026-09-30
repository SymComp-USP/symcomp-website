from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_admin_user, get_current_user
from app.auth.scopes import Scope
from app.core.database import get_session
from app.core.exceptions.app_errors import BadRequestError, NotFoundError
from app.semana import schemas, services
from app.users.models import User

router = APIRouter(prefix="/semanas", tags=["semana"])
admin_router = APIRouter(prefix="/admin/semanas", tags=["admin", "semana"])


@admin_router.get("", response_model=list[schemas.AdminSemanaResponse])
@admin_router.get(
    "/", response_model=list[schemas.AdminSemanaResponse], include_in_schema=False
)
async def list_admin_semanas(
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[User, Security(get_current_admin_user, scopes=[Scope.ADMIN])],
):
    semanas = await services.list_semanas(session, include_admin_relations=True)
    return [
        schemas.AdminSemanaResponse(
            id=semana.id,
            nome=semana.nome,
            ano=semana.ano,
            challenge_count=len(semana.challenges),
            participant_count=len(semana.participants),
        )
        for semana in semanas
    ]


@admin_router.post("", response_model=schemas.AdminSemanaResponse, status_code=201)
@admin_router.post(
    "/",
    response_model=schemas.AdminSemanaResponse,
    include_in_schema=False,
    status_code=201,
)
async def create_admin_semana(
    data: schemas.AdminSemanaCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[User, Security(get_current_admin_user, scopes=[Scope.ADMIN])],
):
    semana = await services.create_semana(session, data.nome, data.ano)
    await session.commit()
    return schemas.AdminSemanaResponse.model_validate(semana)


@admin_router.patch("/{semana_id}", response_model=schemas.AdminSemanaResponse)
async def update_admin_semana(
    semana_id: int,
    data: schemas.AdminSemanaUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[User, Security(get_current_admin_user, scopes=[Scope.ADMIN])],
):
    semana = await services.get_semana(session, semana_id)
    if semana is None:
        raise NotFoundError("Semana not found.")
    await services.update_semana(session, semana, nome=data.nome, ano=data.ano)
    await session.commit()
    return schemas.AdminSemanaResponse.model_validate(semana)


@admin_router.delete("/{semana_id}", status_code=204)
async def delete_admin_semana(
    semana_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[User, Security(get_current_admin_user, scopes=[Scope.ADMIN])],
):
    semana = await services.get_semana(session, semana_id)
    if semana is None:
        raise NotFoundError("Semana not found.")
    if semana.challenges or semana.participants:
        raise BadRequestError("Cannot delete a Semana with challenges or participants.")
    await session.delete(semana)
    await session.commit()


@router.get("", response_model=list[schemas.SemanaResponse])
@router.get("/", response_model=list[schemas.SemanaResponse], include_in_schema=False)
async def list_semanas(session: Annotated[AsyncSession, Depends(get_session)]):
    return await services.list_semanas(session)


@router.post(
    "/{semana_id}/join",
    response_model=schemas.SemanaParticipantResponse,
)
async def join_semana(
    semana_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[
        User, Security(get_current_user, scopes=[Scope.PROFILE, Scope.EMAIL])
    ],
):
    semana = await services.get_semana(session, semana_id)
    if semana is None:
        raise NotFoundError("Semana not found.")
    participant = await services.get_or_create_participant(
        session, semana, current_user
    )
    return schemas.SemanaParticipantResponse(
        id=participant.id,
        semana_id=participant.semana_id,
        user_id=participant.user_id,
        nickname=participant.nickname,
    )


@router.get("/{semana_id}/ranking", response_model=list[schemas.SemanaRankingEntry])
async def get_semana_ranking(
    semana_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    if await services.get_semana(session, semana_id) is None:
        raise NotFoundError("Semana not found.")
    return [
        schemas.SemanaRankingEntry(
            participant_id=row[0], nickname=row[1], points=row[2]
        )
        for row in await services.list_ranking(session, semana_id)
    ]


@admin_router.post(
    "/{semana_id}/participants/{participant_id}/points",
    response_model=schemas.PointEventResponse,
)
async def award_points(
    semana_id: int,
    participant_id: UUID,
    data: schemas.PointAdjustment,
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[User, Security(get_current_admin_user, scopes=[Scope.ADMIN])],
):
    participant = await services.get_participant(session, semana_id, participant_id)
    if participant is None:
        raise NotFoundError("Semana participant not found.")
    return await services.add_points(
        session,
        participant,
        data.amount,
        source_type="manual",
        reason=data.reason,
    )
