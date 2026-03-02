"""seed default words

Revision ID: 20260227_0002
Revises: 20260227_0001
Create Date: 2026-02-27 00:00:02
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260227_0002"
down_revision = "20260227_0001"
branch_labels = None
depends_on = None


def upgrade():
    words_table = sa.table(
        "words",
        sa.column("lang", sa.String(length=10)),
        sa.column("content", sa.String(length=255)),
        sa.column("taboos", sa.JSON()),
    )

    op.bulk_insert(
        words_table,
        [
            {"lang": "ES", "content": "casa", "taboos": ["hogar", "techo", "vivienda"]},
            {"lang": "ES", "content": "perro", "taboos": ["animal", "mascota", "can"]},
            {"lang": "ES", "content": "escuela", "taboos": ["colegio", "clase", "profesor"]},
            {"lang": "ES", "content": "auto", "taboos": ["coche", "vehiculo", "conducir"]},
            {"lang": "EN", "content": "house", "taboos": ["home", "roof", "building"]},
            {"lang": "EN", "content": "dog", "taboos": ["animal", "pet", "canine"]},
            {"lang": "EN", "content": "school", "taboos": ["class", "teacher", "students"]},
            {"lang": "EN", "content": "car", "taboos": ["vehicle", "drive", "engine"]},
        ],
    )


def downgrade():
    op.execute(
        sa.text(
            """
            DELETE FROM words
            WHERE (lang, content) IN (
                ('ES', 'casa'),
                ('ES', 'perro'),
                ('ES', 'escuela'),
                ('ES', 'auto'),
                ('EN', 'house'),
                ('EN', 'dog'),
                ('EN', 'school'),
                ('EN', 'car')
            )
            """
        )
    )
