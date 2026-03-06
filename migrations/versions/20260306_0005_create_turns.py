"""create turns

Revision ID: 20260306_0005
Revises: 20260304_0004
Create Date: 2026-03-06 00:00:05
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260306_0005"
down_revision = "20260304_0004"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "turns",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ends_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], name="fk_turns_game_id_games"),
        sa.ForeignKeyConstraint(["player_id"], ["plays.id"], name="fk_turns_player_id_plays"),
    )
    op.create_index("ix_turns_id", "turns", ["id"], unique=False)


def downgrade():
    op.drop_index("ix_turns_id", table_name="turns")
    op.drop_table("turns")
