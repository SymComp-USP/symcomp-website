from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import TimestampsMixin, UUIDPKMixin
from app.core.models import Base

if TYPE_CHECKING:
    from app.users.username.models import Username


class User(Base, UUIDPKMixin, TimestampsMixin):
    """Conta de um participante da semana (login, perfil básico).

    Herda de UUIDPKMixin e TimestampsMixin, que já fornecem:
    - id (UUID, PK)
    - created_at, updated_at, deleted_at (soft delete)

    __tablename__ não é declarado: Base gera "users" automaticamente
    a partir do nome da classe ("User" -> "users").
    """

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Nullable: usuários criados via OAuth (feature futura do módulo `auth`)
    # podem não ter senha própria.
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_admin: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    username_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("usernames.id"), unique=True, nullable=True
    )
    username: Mapped[Username | None] = relationship(
        "Username", back_populates="user", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
