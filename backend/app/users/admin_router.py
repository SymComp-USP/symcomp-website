from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_admin_user
from app.auth.scopes import Scope
from app.core.database import get_session
from app.core.exceptions.app_errors import NotFoundError
from app.core.pagination import Page, PaginationParams
from app.users import services
from app.users.models import User
from app.users.schemas import AdminUserCreate, AdminUserUpdate, UserRead

router = APIRouter(tags=["admin", "users"])

# Reaproveita o sistema de admin já existente (get_current_admin_user + escopo admin)
AdminUser = Annotated[User, Security(get_current_admin_user, scopes=[Scope.ADMIN])]


async def _get_user_or_404(
    session: AsyncSession, user_id: UUID, *, include_deleted: bool
) -> User:
    user = await services.get_user_by_id(session, user_id)

    if user is None and include_deleted:
        user = await services.get_deleted_user_by_id(session, user_id)

    if user is None:
        raise NotFoundError("User not found.")

    return user


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@router.post(
    "/",
    response_model=UserRead,
    include_in_schema=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_in: AdminUserCreate,
    _: AdminUser,
):
    """Cria um usuário, podendo definir `is_admin` e `is_verified`."""
    user = await services.admin_create_user(session, user_in)
    await session.commit()
    return user


@router.get("", response_model=Page[UserRead])
@router.get("/", response_model=Page[UserRead], include_in_schema=False)
async def list_users(
    session: Annotated[AsyncSession, Depends(get_session)],
    pagination: Annotated[PaginationParams, Depends()],
    _: AdminUser,
    include_deleted: bool = False,
):
    """Lista usuários paginados. Soft-deletados só aparecem com `include_deleted`."""
    return await services.list_users_paginated(session, pagination, include_deleted)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: UUID,
    _: AdminUser,
):
    """Busca um usuário por id, inclusive se estiver soft-deletado."""
    return await _get_user_or_404(session, user_id, include_deleted=True)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: UUID,
    user_in: AdminUserUpdate,
    _: AdminUser,
):
    """Atualiza campos de um usuário ativo, inclusive `is_admin` e `is_verified`."""
    user = await _get_user_or_404(session, user_id, include_deleted=False)
    updated_user = await services.update_user(session, user, user_in)
    await session.commit()
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: UUID,
    _: AdminUser,
):
    """Soft delete. Responde 400 se o usuário já estiver deletado."""
    user = await _get_user_or_404(session, user_id, include_deleted=True)
    await services.delete_user(session, user)
    await session.commit()
