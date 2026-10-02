from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, String, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import TimestampsMixin, UUIDPKMixin
from app.core.models import Base

if TYPE_CHECKING:
    from app.challenges.models.input import Input
    from app.challenges.models.question import Question
    from app.semana.models import Semana


class ChallengeScoringType(StrEnum):
    QUIZ = "quiz"
    INPUT = "input"
    MANUAL = "manual"


class Challenge(Base, UUIDPKMixin, TimestampsMixin):
    __tablename__ = "challenges"

    title: Mapped[str] = mapped_column(String(255))
    points_value: Mapped[int] = mapped_column(default=0)
    scoring_type: Mapped[ChallengeScoringType] = mapped_column(
        SQLEnum(ChallengeScoringType, native_enum=False, length=20),
        default=ChallengeScoringType.QUIZ,
        nullable=False,
    )

    finishes_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC) + timedelta(days=1),
        server_default=text("now() + interval '1 day'"),
        nullable=False,
        sort_order=9997,
    )

    image_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    resource_urls: Mapped[list[str]] = mapped_column(JSON, default=list)

    semana_id: Mapped[int | None] = mapped_column(
        ForeignKey("semana_event.id"), nullable=True
    )

    input: Mapped[Input | None] = relationship(
        "Input", back_populates="challenge", cascade="all, delete-orphan", uselist=False
    )
    questions: Mapped[list[Question]] = relationship(back_populates="challenge")
    semana: Mapped[Semana | None] = relationship(back_populates="challenges")
