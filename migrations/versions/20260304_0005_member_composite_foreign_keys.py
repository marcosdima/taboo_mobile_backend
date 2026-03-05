"""member composite foreign keys

Revision ID: 20260304_0005
Revises: 20260304_0004
Create Date: 2026-03-04 00:00:05
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260304_0005"
down_revision = "20260304_0004"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_enforce_member_play_group_same_game ON members;"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS enforce_member_play_group_same_game();"))

    op.add_column("members", sa.Column("game_id", sa.Integer(), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE members AS m
            SET game_id = p.game_id
            FROM plays AS p
            WHERE p.id = m.play_id
            """
        )
    )

    op.alter_column("members", "game_id", nullable=False)

    op.create_unique_constraint("unique_play_id_game", "plays", ["id", "game_id"])
    op.create_unique_constraint("unique_group_id_game", "groups", ["id", "game_id"])

    op.drop_constraint("fk_members_play_id_plays", "members", type_="foreignkey")
    op.drop_constraint("fk_members_group_id_groups", "members", type_="foreignkey")

    op.create_foreign_key("fk_members_game_id_games", "members", "games", ["game_id"], ["id"])
    op.create_foreign_key(
        "fk_members_play_game_plays",
        "members",
        "plays",
        ["play_id", "game_id"],
        ["id", "game_id"],
    )
    op.create_foreign_key(
        "fk_members_group_game_groups",
        "members",
        "groups",
        ["group_id", "game_id"],
        ["id", "game_id"],
    )


def downgrade():
    op.drop_constraint("fk_members_group_game_groups", "members", type_="foreignkey")
    op.drop_constraint("fk_members_play_game_plays", "members", type_="foreignkey")
    op.drop_constraint("fk_members_game_id_games", "members", type_="foreignkey")

    op.create_foreign_key("fk_members_play_id_plays", "members", "plays", ["play_id"], ["id"])
    op.create_foreign_key("fk_members_group_id_groups", "members", "groups", ["group_id"], ["id"])

    op.drop_constraint("unique_group_id_game", "groups", type_="unique")
    op.drop_constraint("unique_play_id_game", "plays", type_="unique")

    op.drop_column("members", "game_id")

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
