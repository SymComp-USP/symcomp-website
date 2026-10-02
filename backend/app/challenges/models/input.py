from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import UUIDPKMixin
from app.core.models import Base

if TYPE_CHECKING:
    from app.challenges.models.challenge import Challenge


class Input(Base, UUIDPKMixin):
    __tablename__ = "inputs"

    prompt: Mapped[str] = mapped_column(String(5000))
    input_answer: Mapped[str | None] = mapped_column(String(255), nullable=True)

    challenge_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"), unique=True
    )
    challenge: Mapped[Challenge] = relationship("Challenge", back_populates="input")
