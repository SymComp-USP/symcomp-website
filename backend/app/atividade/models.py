from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import TimestampsMixin, UUIDPKMixin
from app.core.models import Base

if TYPE_CHECKING:
    from app.semana.models import Semana
    from app.users.models import User


class StatusAtividade(StrEnum):
    PROVISORIA = "provisoria"
    CONFIRMADA = "confirmada"


class TipoAtividade(StrEnum):
    PALESTRA = "palestra"
    WORKSHOP = "workshop"
    ENCERRAMENTO = "encerramento"
    CONVERSA = "conversa"
    COFFEE_BREAK = "coffee_break"


class Atividade(Base, UUIDPKMixin, TimestampsMixin):
    __tablename__ = "atividades"

    semana_id: Mapped[int] = mapped_column(
        ForeignKey("semana_event.id", ondelete="CASCADE"), index=True
    )
    tipo: Mapped[TipoAtividade] = mapped_column(nullable=False)
    titulo: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    status: Mapped[StatusAtividade] = mapped_column(
        default=StatusAtividade.PROVISORIA, nullable=False
    )
    comeca_as: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    termina_as: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    codigo: Mapped[str] = mapped_column(String(4), nullable=False)
    pontos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    horas: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    semana: Mapped[Semana] = relationship(back_populates="atividades")
    presencas: Mapped[list[Presenca]] = relationship(
        back_populates="atividade", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("semana_id", "codigo", name="uq_atividade_semana_codigo"),
        Index("ix_atividade_semana_schedule", "semana_id", "comeca_as"),
    )


class Presenca(Base, UUIDPKMixin, TimestampsMixin):
    __tablename__ = "presencas"

    atividade_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("atividades.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    horas: Mapped[int] = mapped_column(Integer, nullable=False)

    atividade: Mapped[Atividade] = relationship(back_populates="presencas")
    user: Mapped[User | None] = relationship()

    __table_args__ = (
        UniqueConstraint("atividade_id", "user_id", name="uq_presenca_atividade_user"),
        UniqueConstraint("atividade_id", "email", name="uq_presenca_atividade_email"),
    )
