"""add oauth subject to users

Revision ID: f7c2d9a4e1b6
Revises: e0bee973af24
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f7c2d9a4e1b6"
down_revision: str | Sequence[str] | None = "e0bee973af24"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("oauth_subject", sa.String(length=255), nullable=True)
    )
    op.create_unique_constraint(
        "users_oauth_identity_key", "users", ["oauth_provider", "oauth_subject"]
    )


def downgrade() -> None:
    op.drop_constraint("users_oauth_identity_key", "users", type_="unique")
    op.drop_column("users", "oauth_subject")
