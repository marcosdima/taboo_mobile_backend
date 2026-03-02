"""create all tables

Revision ID: 20260227_0001
Revises:
Create Date: 2026-02-27 00:00:01
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260227_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("alias", sa.String(length=50), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=128), nullable=False),
    )

    # Create games table
    op.create_table(
        "games",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("creator", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["creator"], ["users.id"], name="fk_games_creator_users"),
    )
    op.create_index("ix_games_id", "games", ["id"], unique=False)

    # Create plays table
    op.create_table(
        "plays",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_plays_user_id_users"),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], name="fk_plays_game_id_games"),
        sa.UniqueConstraint("user_id", "game_id", name="unique_user_game"),
    )
    op.create_index("ix_plays_id", "plays", ["id"], unique=False)

    # Create words table
    op.create_table(
        "words",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("lang", sa.String(length=10), nullable=False),
        sa.Column("content", sa.String(length=255), nullable=False),
        sa.Column("taboos", sa.JSON(), nullable=False),
        sa.UniqueConstraint("lang", "content", name="unique_lang_content"),
        sa.CheckConstraint("length(trim(content)) > 0", name="content_not_empty"),
        sa.CheckConstraint("length(trim(lang)) > 0", name="lang_not_empty"),
    )
    op.create_index("ix_words_id", "words", ["id"], unique=False)


def downgrade():
    op.drop_index("ix_words_id", table_name="words")
    op.drop_table("words")
    op.drop_index("ix_plays_id", table_name="plays")
    op.drop_table("plays")
    op.drop_index("ix_games_id", table_name="games")
    op.drop_table("games")
    op.drop_table("users")
