"""move username assignment from participants to users

Revision ID: b84e1b2f6a90
Revises: 597d02678cf0
Create Date: 2026-09-27 23:10:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b84e1b2f6a90"
down_revision: str | Sequence[str] | None = "597d02678cf0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "users_username_id_fkey", "users", "usernames", ["username_id"], ["id"]
    )
    op.create_unique_constraint("users_username_id_key", "users", ["username_id"])

    op.execute(
        sa.text(
            """
            WITH ranked_assignments AS (
                SELECT
                    user_id,
                    username_id,
                    row_number() OVER (
                        PARTITION BY user_id ORDER BY created_at, id
                    ) AS user_rank,
                    row_number() OVER (
                        PARTITION BY username_id ORDER BY created_at, id
                    ) AS username_rank
                FROM challenge_participants
                WHERE username_id IS NOT NULL
            )
            UPDATE users
            SET username_id = ranked_assignments.username_id
            FROM ranked_assignments
            WHERE users.id = ranked_assignments.user_id
              AND ranked_assignments.user_rank = 1
              AND ranked_assignments.username_rank = 1
            """
        )
    )

    op.drop_constraint(
        "uq_participant_username_challenge",
        "challenge_participants",
        type_="unique",
    )
    op.drop_constraint(
        "challenge_participants_username_id_fkey",
        "challenge_participants",
        type_="foreignkey",
    )
    op.drop_column("challenge_participants", "username_id")


def downgrade() -> None:
    op.add_column(
        "challenge_participants",
        sa.Column("username_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "challenge_participants_username_id_fkey",
        "challenge_participants",
        "usernames",
        ["username_id"],
        ["id"],
    )
    op.create_unique_constraint(
        "uq_participant_username_challenge",
        "challenge_participants",
        ["challenge_id", "username_id"],
    )
    op.execute(
        sa.text(
            """
            UPDATE challenge_participants
            SET username_id = users.username_id
            FROM users
            WHERE challenge_participants.user_id = users.id
            """
        )
    )
    op.drop_constraint("users_username_id_key", "users", type_="unique")
    op.drop_constraint("users_username_id_fkey", "users", type_="foreignkey")
    op.drop_column("users", "username_id")
