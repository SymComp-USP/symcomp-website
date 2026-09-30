"""create activities and attendance"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "4e2f7a9b1c3d"
down_revision: str | Sequence[str] | None = "1f4a9d2b7c11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "atividades",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("semana_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("comeca_as", sa.DateTime(timezone=True), nullable=False),
        sa.Column("termina_as", sa.DateTime(timezone=True), nullable=False),
        sa.Column("codigo", sa.String(length=4), nullable=False),
        sa.Column("pontos", sa.Integer(), server_default="0", nullable=False),
        sa.Column("horas", sa.Integer(), server_default="1", nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("semana_id", "codigo", name="uq_atividade_semana_codigo"),
    )
    op.create_index(
        "ix_atividades_semana_id", "atividades", ["semana_id"], unique=False
    )
    op.create_index(
        "ix_atividade_semana_schedule",
        "atividades",
        ["semana_id", "comeca_as"],
        unique=False,
    )

    op.create_table(
        "presencas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("atividade_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("horas", sa.Integer(), nullable=False),
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
            ["atividade_id"], ["atividades.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "atividade_id", "user_id", name="uq_presenca_atividade_user"
        ),
        sa.UniqueConstraint(
            "atividade_id", "email", name="uq_presenca_atividade_email"
        ),
    )
    op.create_index(
        "ix_presencas_atividade_id", "presencas", ["atividade_id"], unique=False
    )
    op.create_index("ix_presencas_user_id", "presencas", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("presencas")
    op.drop_index("ix_atividade_semana_schedule", table_name="atividades")
    op.drop_index("ix_atividades_semana_id", table_name="atividades")
    op.drop_table("atividades")
