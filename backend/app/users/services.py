import asyncio
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import hash_password
from app.core.pagination import Page, PaginationParams
from app.users.exceptions import UserAlreadyDeletedError, UserAlreadyExistsError
from app.users.models import User
from app.users.schemas import (
    AdminUserCreate,
    UserCreate,
    UserRead,
    UserUpdate,
)


# --- buscas "normais": ignoram usuários soft-deletados ---
async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await session.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def get_user_profile_by_id(
    session: AsyncSession, user_id: uuid.UUID
) -> User | None:
    result = await session.execute(
        select(User)
        .where(User.id == user_id, User.deleted_at.is_(None))
        .execution_options(populate_existing=True)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(
        select(User).where(User.email == email, User.deleted_at.is_(None))
    )

    print(result)

    return result.scalar_one_or_none()


# --- buscas explícitas por usuários deletados ---


async def get_deleted_user_by_id(
    session: AsyncSession, user_id: uuid.UUID
) -> User | None:
    # Busca um usuário soft-deletado por ID.
    # Retorna None se o usuário não existir ou se existir mas não estiver deletado.
    result = await session.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_not(None))
    )
    return result.scalar_one_or_none()


async def get_deleted_user_by_email(session: AsyncSession, email: str) -> User | None:
    # Busca um usuário soft-deletado por Email.
    # Retorna None se o usuário não existir ou se existir mas não estiver deletado.
    result = await session.execute(
        select(User).where(User.email == email, User.deleted_at.is_not(None))
    )
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, user_in: UserCreate) -> User:
    """Cria um novo usuário a partir de UserCreate.

    - Se já existir uma conta ATIVA com esse e-mail, levanta UserAlreadyExistsError.
    - Se existir uma conta DELETADA (soft-deleted) com esse e-mail, reativa
      essa conta em vez de criar um registro novo (evita duplicar histórico
      de pontuação/participação vinculado ao usuário antigo).

    Não faz commit.
    """
    existing_user = await get_user_by_email(session, user_in.email)
    if existing_user is not None:
        raise UserAlreadyExistsError(user_in.email)

    deleted_user = await get_deleted_user_by_email(session, user_in.email)
    if deleted_user is not None:
        deleted_user.deleted_at = None
        deleted_user.name = user_in.name
        deleted_user.password_hash = await asyncio.to_thread(
            hash_password, user_in.password
        )

        # Reseta verificações e privilégios
        deleted_user.is_admin = False
        deleted_user.is_verified = False

        await session.flush()
        await session.refresh(deleted_user)

        return deleted_user

    user = User(
        email=user_in.email,
        name=user_in.name,
        password_hash=await asyncio.to_thread(hash_password, user_in.password),
    )

    session.add(user)
    await session.flush()
    await session.refresh(user)

    return user


async def admin_create_user(session: AsyncSession, user_in: AdminUserCreate) -> User:
    """Cria um usuário como admin, podendo definir `is_admin` e `is_verified`.

    Reaproveita `create_user` (mesmas regras de e-mail duplicado, reativação de
    conta deletada e atribuição de username) e aplica os privilégios em seguida.

    Não faz commit.
    """
    user = await create_user(session, user_in)

    user.is_admin = user_in.is_admin
    user.is_verified = user_in.is_verified

    await session.flush()
    await session.refresh(user)

    return user


async def list_users_paginated(
    session: AsyncSession,
    pagination: PaginationParams,
    include_deleted: bool = False,
) -> Page[UserRead]:
    # Lista usuários paginados; por padrão ignora os soft-deletados
    filters = [] if include_deleted else [User.deleted_at.is_(None)]

    total = await session.scalar(select(func.count(User.id)).where(*filters))

    rows = (
        await session.scalars(
            select(User)
            .where(*filters)
            .order_by(User.created_at.desc(), User.id)
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
    ).all()

    return Page[UserRead](
        items=[UserRead.model_validate(u) for u in rows],
        total=total or 0,
        limit=pagination.limit,
        offset=pagination.offset,
    )


async def update_user(session: AsyncSession, user: User, user_in: UserUpdate) -> User:
    # Atualiza o usuario a partir da classe UserUpdate, modifica apenas campos explicitamente enviados
    # (campos enviados como null são ignorados: nenhum deles aceita NULL no banco)
    # Levanta UserAlreadyExistsError se o novo e-mail já pertence a outra conta
    # (ativa ou soft-deletada, pois a unicidade do e-mail vale para ambas).
    # Não faz commit
    if user_in.email is not None and user_in.email != user.email:
        email_taken = await session.scalar(
            select(User.id).where(User.email == user_in.email, User.id != user.id)
        )
        if email_taken is not None:
            raise UserAlreadyExistsError(user_in.email)

    update_data = user_in.model_dump(
        exclude_unset=True, exclude_none=True, exclude={"password"}
    )
    for field, value in update_data.items():
        setattr(user, field, value)

    if user_in.password is not None:
        user.password_hash = await asyncio.to_thread(hash_password, user_in.password)

    await session.flush()
    await session.refresh(user)

    return user


async def delete_user(session: AsyncSession, user: User) -> User:
    # Deleta o usuario definindo o "deleted_at", levanta erro caso usuario já esteja deletado
    # Não faz commit
    if user.deleted_at is not None:
        raise UserAlreadyDeletedError(user.id)

    # revisar uso de timezone depois, não definido nos mixin
    user.deleted_at = datetime.now(UTC).replace(tzinfo=None)

    await session.flush()
    await session.refresh(user)

    return user
