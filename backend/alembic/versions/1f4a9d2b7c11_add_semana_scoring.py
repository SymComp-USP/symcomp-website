"""add Semana participation and point ledger

Revision ID: 1f4a9d2b7c11
Revises: b84e1b2f6a90
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "1f4a9d2b7c11"
down_revision: str | Sequence[str] | None = "b84e1b2f6a90"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "semana_event",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
    )
    op.create_table(
        "semana_participants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("semana_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("nickname", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["semana_id"], ["semana_event.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "semana_id", "user_id", name="uq_semana_participant_event_user"
        ),
        sa.UniqueConstraint(
            "semana_id", "nickname", name="uq_semana_participant_event_nickname"
        ),
    )
    op.create_table(
        "point_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("semana_participant_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=True),
        sa.Column("reason", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["semana_participant_id"], ["semana_participants.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "semana_participant_id",
            "source_type",
            "source_id",
            name="uq_point_event_source",
        ),
    )

    op.add_column(
        "challenges",
        sa.Column("prompt", sa.String(5000), server_default="", nullable=False),
    )
    op.add_column(
        "challenges",
        sa.Column(
            "resource_urls", sa.JSON(), server_default=sa.text("'[]'"), nullable=False
        ),
    )
    op.add_column(
        "challenges",
        sa.Column(
            "points_value", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
    )
    op.add_column(
        "challenges", sa.Column("input_answer", sa.String(255), nullable=True)
    )
    op.add_column("challenges", sa.Column("semana_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "challenges_semana_id_fkey", "challenges", "semana_event", ["semana_id"], ["id"]
    )
    op.add_column(
        "challenge_participants",
        sa.Column("semana_participant_id", sa.Uuid(), nullable=True),
    )
    op.add_column(
        "challenge_participants", sa.Column("submission", sa.String(255), nullable=True)
    )
    op.create_foreign_key(
        "challenge_participants_semana_participant_id_fkey",
        "challenge_participants",
        "semana_participants",
        ["semana_participant_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "challenge_participants_semana_participant_id_fkey",
        "challenge_participants",
        type_="foreignkey",
    )
    op.drop_column("challenge_participants", "submission")
    op.drop_column("challenge_participants", "semana_participant_id")
    op.drop_constraint("challenges_semana_id_fkey", "challenges", type_="foreignkey")
    for column in (
        "semana_id",
        "input_answer",
        "points_value",
        "resource_urls",
        "prompt",
    ):
        op.drop_column("challenges", column)
    op.drop_table("point_events")
    op.drop_table("semana_participants")
    op.drop_table("semana_event")
