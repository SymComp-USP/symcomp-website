from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import TimestampsMixin, UUIDPKMixin
from app.core.models import Base

if TYPE_CHECKING:
    from app.challenges.models.challenge import Challenge
    from app.challenges.models.challenge_participant import ChallengeParticipant
    from app.users.models import User


class SemanaEvent(Base):
    __tablename__ = "semana_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255))
    ano: Mapped[int] = mapped_column()

    challenges: Mapped[list[Challenge]] = relationship(back_populates="semana")
    participants: Mapped[list[SemanaParticipant]] = relationship(
        back_populates="semana", cascade="all, delete-orphan"
    )


class SemanaParticipant(Base, UUIDPKMixin, TimestampsMixin):
    __tablename__ = "semana_participants"

    semana_id: Mapped[int] = mapped_column(
        ForeignKey("semana_event.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    nickname: Mapped[str] = mapped_column(String(255))

    semana: Mapped[SemanaEvent] = relationship(back_populates="participants")
    user: Mapped[User] = relationship()
    challenge_attempts: Mapped[list[ChallengeParticipant]] = relationship(
        back_populates="semana_participant"
    )
    point_events: Mapped[list[PointEvent]] = relationship(
        back_populates="semana_participant", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("semana_id", "user_id"),
        UniqueConstraint("semana_id", "nickname"),
    )


class PointEvent(Base, UUIDPKMixin, TimestampsMixin):
    __tablename__ = "point_events"

    semana_participant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("semana_participants.id", ondelete="CASCADE")
    )
    amount: Mapped[int] = mapped_column()
    source_type: Mapped[str] = mapped_column(String(32))
    source_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    semana_participant: Mapped[SemanaParticipant] = relationship(
        back_populates="point_events"
    )

    __table_args__ = (
        UniqueConstraint(
            "semana_participant_id", "source_type", "source_id",
            name="uq_point_event_source",
        ),
    )
