from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import TimestampsMixin, UUIDPKMixin
from app.core.models import Base

from .question import Question

if TYPE_CHECKING:
    from .challenge_participant import ChallengeParticipant


class Answer(Base, UUIDPKMixin, TimestampsMixin):
    """Registro da resposta de um usuário a uma questão de desafio"""

    participant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("challenge_participants.id", ondelete="CASCADE")
    )
    participant: Mapped[ChallengeParticipant] = relationship(
        back_populates="answers",
    )

    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE")
    )
    question: Mapped[Question] = relationship()
    content: Mapped[str] = mapped_column(String(255))

    is_correct: Mapped[bool] = mapped_column(Boolean)

    __table_args__ = (
        UniqueConstraint(
            "participant_id", "question_id", name="uq_participant_question"
        ),
    )
