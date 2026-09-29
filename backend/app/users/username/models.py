from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import UUIDPKMixin
from app.core.models import Base

if TYPE_CHECKING:
    from app.semana.models import SemanaParticipant


class UsernameMother(Base, UUIDPKMixin):
    __tablename__ = "username_mothers"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[str] = mapped_column(String(201), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class Username(Base, UUIDPKMixin):
    __tablename__ = "usernames"

    nickname: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    first_mother_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("username_mothers.id"), nullable=False
    )
    last_mother_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("username_mothers.id"), nullable=False
    )

    first_mother: Mapped[UsernameMother] = relationship(foreign_keys=[first_mother_id])
    last_mother: Mapped[UsernameMother] = relationship(foreign_keys=[last_mother_id])
    participants: Mapped[list[SemanaParticipant]] = relationship(
        "SemanaParticipant", back_populates="username"
    )
