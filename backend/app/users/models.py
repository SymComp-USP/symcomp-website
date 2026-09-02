from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampsMixin, UUIDPKMixin
from app.core.models import Base


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

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
