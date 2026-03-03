"""enforce max plays per game at db level

Revision ID: 20260303_0003
Revises: 20260227_0002
Create Date: 2026-03-03 00:00:03
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260303_0003"
down_revision = "20260227_0002"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        sa.text(
            """
            CREATE OR REPLACE FUNCTION enforce_max_plays_per_game()
            RETURNS trigger
            AS $$
            BEGIN
                IF (SELECT COUNT(*) FROM plays WHERE game_id = NEW.game_id) >= 10 THEN
                    RAISE EXCEPTION 'Game already has maximum of 10 plays'
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
            CREATE TRIGGER trg_enforce_max_plays_per_game
            BEFORE INSERT ON plays
            FOR EACH ROW
            EXECUTE FUNCTION enforce_max_plays_per_game();
            """
        )
    )


def downgrade():
    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_enforce_max_plays_per_game ON plays;"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS enforce_max_plays_per_game();"))
