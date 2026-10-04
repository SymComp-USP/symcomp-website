"""add description to challenges

Revision ID: 4f21ac9d7b30
Revises: 7e2b0a1c4d5f
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "4f21ac9d7b30"
down_revision: str | Sequence[str] | None = "7e2b0a1c4d5f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "challenges",
        sa.Column("description", sa.Text(), server_default="", nullable=False),
    )
    op.alter_column("challenges", "description", server_default=None)


def downgrade() -> None:
    op.drop_column("challenges", "description")
