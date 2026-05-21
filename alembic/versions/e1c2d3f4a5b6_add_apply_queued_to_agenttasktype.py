"""add apply_queued to agenttasktype

Revision ID: e1c2d3f4a5b6
Revises: f9a5c2b3d1e6
Create Date: 2026-05-01 08:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'e1c2d3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'f9a5c2b3d1e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_enum e
                    JOIN pg_type t ON t.oid = e.enumtypid
                    WHERE t.typname = 'agenttasktype' AND e.enumlabel = 'APPLY_QUEUED'
                ) THEN
                    ALTER TYPE agenttasktype ADD VALUE 'APPLY_QUEUED';
                END IF;
            END
            $$;
            """
        )
    )


def downgrade() -> None:
    # PostgreSQL does not support removing enum labels directly.
    # Keep downgrade as a no-op for safety.
    pass