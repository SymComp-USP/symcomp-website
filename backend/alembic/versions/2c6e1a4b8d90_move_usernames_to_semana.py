"""move username ownership to Semana participants

Revision ID: 2c6e1a4b8d90
Revises: 1f4a9d2b7c11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "2c6e1a4b8d90"
down_revision: str | Sequence[str] | None = "1f4a9d2b7c11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "semana_participants", sa.Column("username_id", sa.Uuid(), nullable=True)
    )
    op.create_foreign_key(
        "semana_participants_username_id_fkey",
        "semana_participants",
        "usernames",
        ["username_id"],
        ["id"],
    )
    op.execute(
        sa.text(
            """
            UPDATE semana_participants AS participants
            SET username_id = users.username_id
            FROM users
            WHERE participants.user_id = users.id
              AND users.username_id IS NOT NULL
            """
        )
    )
    op.create_unique_constraint(
        "uq_semana_participant_username",
        "semana_participants",
        ["semana_id", "username_id"],
    )
    op.drop_column("semana_participants", "nickname")
    op.drop_constraint("users_username_id_key", "users", type_="unique")
    op.drop_constraint("users_username_id_fkey", "users", type_="foreignkey")
    op.drop_column("users", "username_id")


def downgrade() -> None:
    op.add_column("users", sa.Column("username_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "users_username_id_fkey", "users", "usernames", ["username_id"], ["id"]
    )
    op.create_unique_constraint("users_username_id_key", "users", ["username_id"])
    op.add_column(
        "semana_participants",
        sa.Column("nickname", sa.String(255), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE users
            SET username_id = participants.username_id
            FROM semana_participants AS participants
            WHERE users.id = participants.user_id
              AND participants.username_id IS NOT NULL
            """
        )
    )
    op.drop_constraint(
        "uq_semana_participant_username", "semana_participants", type_="unique"
    )
    op.drop_constraint(
        "semana_participants_username_id_fkey",
        "semana_participants",
        type_="foreignkey",
    )
    op.drop_column("semana_participants", "username_id")
