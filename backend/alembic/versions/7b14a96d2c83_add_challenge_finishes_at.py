"""add challenge finish deadline

Revision ID: 7b14a96d2c83
Revises: c8389c55b075
Create Date: 2026-09-27 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7b14a96d2c83"
down_revision: str | Sequence[str] | None = "c8389c55b075"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "challenges",
        sa.Column(
            "finishes_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now() + interval '1 day'"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("challenges", "finishes_at")
