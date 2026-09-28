from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import TimestampsMixin, UUIDPKMixin
from app.core.models import Base

if TYPE_CHECKING:
    from app.challenges.models.challenge import Challenge


class Question(Base, UUIDPKMixin):
    __tablename__ = "questions"

    prompt: Mapped[str] = mapped_column(String(5000))
    answer: Mapped[str] = mapped_column(String(255))
    points_value: Mapped[int] = mapped_column(default=0)

    challenge_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("challenges.id"))
    challenge: Mapped[Challenge] = relationship(back_populates="questions")
