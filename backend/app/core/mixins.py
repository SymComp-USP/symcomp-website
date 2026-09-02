import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class UUIDPKMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, sort_order=-1
    )


class TimestampsMixin:
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), sort_order=9997
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=None, onupdate=func.now(), sort_order=9998
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        default=None, index=True, sort_order=9999
    )
