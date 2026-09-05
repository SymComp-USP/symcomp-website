import asyncio
import uuid
from datetime import UTC, datetime

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate

# --- funções de autenticação ---
# Inicialização da biblioteca de hash
ph = PasswordHash((Argon2Hasher(),))


# Função de criar hash
def hash_password(password: str) -> str:
    return ph.hash(password)


# Função de verificação da hash
def verify_password(plain_password, hashed_password):
    return ph.verify(plain_password, hashed_password)


# --- classes de erro ---
class UserAlreadyDeletedError(Exception):
    """Levantado ao tentar deletar (soft delete) um usuário que já está
    marcado como deletado."""

    def __init__(self, user_id: uuid.UUID) -> None:
        self.user_id = user_id
        super().__init__(f"User with id {user_id!r} is already deleted")


class UserAlreadyExistsError(Exception):
    """Levantado ao tentar criar um usuário com um e-mail já cadastrado
    e ainda ativo (não deletado)."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User with email {email!r} already exists")


# --- buscas "normais": ignoram usuários soft-deletados ---
async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await session.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(
        select(User).where(User.email == email, User.deleted_at.is_(None))
    )
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


async def update_user(session: AsyncSession, user: User, user_in: UserUpdate) -> User:
    # Atualiza o usuario a partir da classe UserUpdate, modifica apenas campos explicitamente enviados
    # Não faz commit
    update_data = user_in.model_dump(exclude_unset=True, exclude={"password"})
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
