"""add auth token creation timestamp

Revision ID: 3b5d9f7e2a41
Revises: 2a4c8e6d1f90
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "3b5d9f7e2a41"
down_revision: str | Sequence[str] | None = "2a4c8e6d1f90"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "auth_tokens",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("auth_tokens", "created_at")
