from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.atividade import schemas, services
from app.auth.dependencies import get_current_admin_user, get_optional_current_user
from app.auth.scopes import Scope
from app.core.database import get_session
from app.core.exceptions.app_errors import NotFoundError
from app.semana.services import get_semana
from app.users.models import User

router = APIRouter(prefix="/semanas/{semana_id}/atividades", tags=["atividade"])
attendance_router = APIRouter(
    prefix="/semanas/{semana_id}/atividades", tags=["atividade"]
)
admin_router = APIRouter(
    prefix="/admin/semanas/{semana_id}/atividades", tags=["admin", "atividade"]
)


async def _require_semana(session: AsyncSession, semana_id: int):
    semana = await get_semana(session, semana_id)
    if semana is None:
        raise NotFoundError("Semana not found.")
    return semana


@router.get("", response_model=list[schemas.AtividadeResponse])
@router.get(
    "/", response_model=list[schemas.AtividadeResponse], include_in_schema=False
)
async def list_atividades(
    semana_id: int, session: Annotated[AsyncSession, Depends(get_session)]
):
    await _require_semana(session, semana_id)
    return await services.list_atividades(session, semana_id)


@admin_router.get("", response_model=list[schemas.AtividadeResponse])
@admin_router.get(
    "/", response_model=list[schemas.AtividadeResponse], include_in_schema=False
)
async def list_admin_atividades(
    semana_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[User, Security(get_current_admin_user, scopes=[Scope.ADMIN])],
):
    await _require_semana(session, semana_id)
    return await services.list_atividades(session, semana_id)


@admin_router.post("", response_model=schemas.AtividadeResponse, status_code=201)
async def create_admin_atividade(
    semana_id: int,
    data: schemas.AtividadeCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[User, Security(get_current_admin_user, scopes=[Scope.ADMIN])],
):
    semana = await _require_semana(session, semana_id)
    return await services.create_atividade(session, semana, **data.model_dump())


@admin_router.patch("/{atividade_id}", response_model=schemas.AtividadeResponse)
async def update_admin_atividade(
    semana_id: int,
    atividade_id: UUID,
    data: schemas.AtividadeUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[User, Security(get_current_admin_user, scopes=[Scope.ADMIN])],
):
    atividade = await services.get_atividade(session, semana_id, atividade_id)
    if atividade is None:
        raise NotFoundError("Activity not found.")
    return await services.update_atividade(session, atividade, data.model_dump())


@admin_router.delete("/{atividade_id}", status_code=204)
async def delete_admin_atividade(
    semana_id: int,
    atividade_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[User, Security(get_current_admin_user, scopes=[Scope.ADMIN])],
):
    atividade = await services.get_atividade(session, semana_id, atividade_id)
    if atividade is None:
        raise NotFoundError("Activity not found.")
    await session.delete(atividade)


@attendance_router.post(
    "/registrar/{codigo}",
    response_model=schemas.PresencaResponse,
)
async def register_atividade_presence(
    semana_id: int,
    codigo: Annotated[str, Path(pattern=r"^\d{4}$")],
    data: schemas.PresencaRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User | None, Depends(get_optional_current_user)],
):
    await _require_semana(session, semana_id)
    atividade = await services.get_atividade_by_codigo(session, semana_id, codigo)
    if atividade is None:
        raise NotFoundError("Activity not found.")
    presence, points = await services.register_presence(
        session, atividade, user, data.nome, data.email
    )
    return schemas.PresencaResponse(
        atividade_id=presence.atividade_id,
        pontos_adicionados=points,
        horas=presence.horas,
    )
