"""add challenge start time

Revision ID: b81f3c2a6d40
Revises: 4f21ac9d7b30
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b81f3c2a6d40"
down_revision: str | Sequence[str] | None = "4f21ac9d7b30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "challenges",
        sa.Column(
            "starts_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("challenges", "starts_at")
