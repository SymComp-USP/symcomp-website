"""add activity schedule details

Revision ID: 9f1d7a2c4b6e
Revises: 508a25128b6c
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "9f1d7a2c4b6e"
down_revision: str | Sequence[str] | None = "508a25128b6c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("atividades", sa.Column("descricao", sa.String(length=5000)))
    op.add_column("atividades", sa.Column("local", sa.String(length=255)))
    op.add_column(
        "atividades",
        sa.Column(
            "palestrantes", sa.JSON(), nullable=False, server_default=sa.text("'[]'")
        ),
    )
    op.add_column("atividades", sa.Column("link_live", sa.String(length=500)))
    op.alter_column("atividades", "palestrantes", server_default=None)


def downgrade() -> None:
    op.drop_column("atividades", "link_live")
    op.drop_column("atividades", "palestrantes")
    op.drop_column("atividades", "local")
    op.drop_column("atividades", "descricao")
