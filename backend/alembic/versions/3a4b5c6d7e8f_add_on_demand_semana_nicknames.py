"""Store generated nicknames on Semana participants.

Revision ID: 3a4b5c6d7e8f
Revises: 2c6e1a4b8d90
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "3a4b5c6d7e8f"
down_revision: str | Sequence[str] | None = "2c6e1a4b8d90"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "semana_participants",
        sa.Column("nickname", sa.String(length=255), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE semana_participants AS participants
            SET nickname = usernames.nickname
            FROM usernames
            WHERE participants.username_id = usernames.id
              AND participants.nickname IS NULL
            """
        )
    )
    op.execute(
        sa.text(
            """
            WITH numbered AS (
                SELECT
                    id,
                    'Participante' || LPAD(
                        ROW_NUMBER() OVER (
                            PARTITION BY semana_id ORDER BY id
                        )::text,
                        4,
                        '0'
                    ) AS generated_nickname
                FROM semana_participants
                WHERE nickname IS NULL
            )
            UPDATE semana_participants AS participants
            SET nickname = numbered.generated_nickname
            FROM numbered
            WHERE participants.id = numbered.id
            """
        )
    )
    op.create_unique_constraint(
        "uq_semana_participant_nickname",
        "semana_participants",
        ["semana_id", "nickname"],
    )
    op.drop_constraint(
        "uq_semana_participant_username",
        "semana_participants",
        type_="unique",
    )
    op.drop_constraint(
        "semana_participants_username_id_fkey",
        "semana_participants",
        type_="foreignkey",
    )
    op.drop_column("semana_participants", "username_id")
    op.drop_table("usernames")
    op.drop_table("username_mothers")


def downgrade() -> None:
    op.drop_constraint(
        "uq_semana_participant_nickname",
        "semana_participants",
        type_="unique",
    )
    op.drop_column("semana_participants", "nickname")
