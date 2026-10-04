"""move input challenge data into its own table

Revision ID: 7e2b0a1c4d5f
Revises: 9f1d7a2c4b6e
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "7e2b0a1c4d5f"
down_revision: str | Sequence[str] | None = "9f1d7a2c4b6e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "inputs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("prompt", sa.String(length=5000), nullable=False),
        sa.Column("input_answer", sa.String(length=255), nullable=True),
        sa.Column("challenge_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["challenge_id"],
            ["challenges.id"],
            name=op.f("inputs_challenge_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("inputs_pkey")),
        sa.UniqueConstraint("challenge_id", name=op.f("inputs_challenge_id_key")),
    )
    op.execute(
        sa.text(
            """
            UPDATE challenges
            SET points_value = (
                SELECT COALESCE(SUM(questions.points_value), 0)
                FROM questions
                WHERE questions.challenge_id = challenges.id
            )
            WHERE scoring_type = 'QUIZ'
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO inputs (id, prompt, input_answer, challenge_id)
            SELECT gen_random_uuid(), prompt, input_answer, id
            FROM challenges
            WHERE scoring_type = 'INPUT'
            """
        )
    )
    op.drop_column("questions", "points_value")
    op.drop_column("challenges", "input_answer")
    op.drop_column("challenges", "prompt")


def downgrade() -> None:
    op.add_column(
        "challenges",
        sa.Column("prompt", sa.String(length=5000), server_default="", nullable=False),
    )
    op.add_column(
        "challenges", sa.Column("input_answer", sa.String(length=255), nullable=True)
    )
    op.execute(
        sa.text(
            """
            UPDATE challenges
            SET prompt = inputs.prompt, input_answer = inputs.input_answer
            FROM inputs
            WHERE challenges.id = inputs.challenge_id
            """
        )
    )
    op.alter_column("challenges", "prompt", server_default=None)
    op.drop_table("inputs")
    op.add_column(
        "questions",
        sa.Column("points_value", sa.Integer(), server_default="0", nullable=False),
    )
    op.execute(
        sa.text(
            """
            WITH ranked_questions AS (
                SELECT questions.id,
                       challenges.points_value / COUNT(*) OVER (
                           PARTITION BY questions.challenge_id
                       ) AS base_points,
                       challenges.points_value % COUNT(*) OVER (
                           PARTITION BY questions.challenge_id
                       ) AS remainder,
                       ROW_NUMBER() OVER (
                           PARTITION BY questions.challenge_id ORDER BY questions.id
                       ) AS question_number
                FROM questions
                JOIN challenges ON challenges.id = questions.challenge_id
            )
            UPDATE questions
            SET points_value = ranked_questions.base_points +
                CASE WHEN ranked_questions.question_number <= ranked_questions.remainder
                     THEN 1 ELSE 0 END
            FROM ranked_questions
            WHERE questions.id = ranked_questions.id
            """
        )
    )
    op.alter_column("questions", "points_value", server_default=None)
