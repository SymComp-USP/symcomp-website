from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import TimestampsMixin, UUIDPKMixin
from app.core.models import Base
from app.users.models import User

from .challenge import Challenge

if TYPE_CHECKING:
    from .answer import Answer


class ChallengeParticipant(Base, UUIDPKMixin, TimestampsMixin):
    """ChallengeParticipant é uma tabela de agregação entre User e Challenge, com relacionamento 'N para um' com ambos."""

    __tablename__ = "challenge_participants"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    challenge_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("challenges.id"))
    user: Mapped[User] = relationship()
    challenge: Mapped[Challenge] = relationship()

    score: Mapped[int] = mapped_column(default=0)
    answers: Mapped[list[Answer]] = relationship(
        back_populates="participant", cascade="all, delete-orphan"
    )

    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "challenge_id", name="uq_participant_user_challenge"
        ),
    )
