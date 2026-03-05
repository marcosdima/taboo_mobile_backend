"""create groups and members

Revision ID: 20260304_0004
Revises: 20260303_0003
Create Date: 2026-03-04 00:00:04
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260304_0004"
down_revision = "20260303_0003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], name="fk_groups_game_id_games"),
        sa.UniqueConstraint("name", "game_id", name="unique_group_name_game"),
    )
    op.create_index("ix_groups_id", "groups", ["id"], unique=False)

    op.create_table(
        "members",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("play_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["play_id"], ["plays.id"], name="fk_members_play_id_plays"),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], name="fk_members_group_id_groups"),
        sa.UniqueConstraint("play_id", name="unique_member_play"),
    )
    op.create_index("ix_members_id", "members", ["id"], unique=False)

    op.execute(
        sa.text(
            """
            CREATE OR REPLACE FUNCTION enforce_member_play_group_same_game()
            RETURNS trigger
            AS $$
            DECLARE
                play_game_id INTEGER;
                group_game_id INTEGER;
            BEGIN
                SELECT game_id INTO play_game_id
                FROM plays
                WHERE id = NEW.play_id;

                SELECT game_id INTO group_game_id
                FROM groups
                WHERE id = NEW.group_id;

                IF play_game_id IS NULL OR group_game_id IS NULL THEN
                    RAISE EXCEPTION 'Referenced play or group does not exist'
                    USING ERRCODE = '23503';
                END IF;

                IF play_game_id != group_game_id THEN
                    RAISE EXCEPTION 'Play and group must belong to the same game'
                    USING ERRCODE = '23514';
                END IF;

                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TRIGGER trg_enforce_member_play_group_same_game
            BEFORE INSERT OR UPDATE ON members
            FOR EACH ROW
            EXECUTE FUNCTION enforce_member_play_group_same_game();
            """
        )
    )


def downgrade():
    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_enforce_member_play_group_same_game ON members;"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS enforce_member_play_group_same_game();"))

    op.drop_index("ix_members_id", table_name="members")
    op.drop_table("members")

    op.drop_index("ix_groups_id", table_name="groups")
    op.drop_table("groups")
