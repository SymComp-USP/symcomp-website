"""add single-use auth tokens

Revision ID: 2a4c8e6d1f90
Revises: f7c2d9a4e1b6
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "2a4c8e6d1f90"
down_revision: str | Sequence[str] | None = "f7c2d9a4e1b6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "auth_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("purpose", sa.String(length=32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("auth_tokens_user_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("auth_tokens_pkey")),
        sa.UniqueConstraint("token_hash", name=op.f("auth_tokens_token_hash_key")),
    )
    op.create_index(op.f("auth_tokens_user_id_idx"), "auth_tokens", ["user_id"])
    op.create_index(op.f("auth_tokens_purpose_idx"), "auth_tokens", ["purpose"])


def downgrade() -> None:
    op.drop_index(op.f("auth_tokens_purpose_idx"), table_name="auth_tokens")
    op.drop_index(op.f("auth_tokens_user_id_idx"), table_name="auth_tokens")
    op.drop_table("auth_tokens")
