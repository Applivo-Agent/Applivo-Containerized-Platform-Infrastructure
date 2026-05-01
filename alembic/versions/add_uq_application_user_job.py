"""add_unique_constraint_application_user_job

Revision ID: add_uq_application_user_job
Revises: 6df4ff846734
Create Date: 2026-04-04 21:52:00.000000

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = 'add_uq_application_user_job'
down_revision: Union[str, None] = 'security_models_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create unique constraint on applications table
    op.execute(
        text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_constraint
                    WHERE conname = 'uq_application_user_job'
                ) THEN
                    ALTER TABLE applications
                    ADD CONSTRAINT uq_application_user_job
                    UNIQUE (user_id, job_id);
                END IF;
            END
            $$;
            """
        )
    )


def downgrade() -> None:
    op.drop_constraint(
        'uq_application_user_job',
        'applications',
        type_='unique'
    )