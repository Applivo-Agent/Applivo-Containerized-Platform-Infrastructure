"""reconcile missing user-scope columns on jobs and agent_tasks

Revision ID: 2e6f31d4aa10
Revises: 9a2f4a2c5d91
Create Date: 2026-04-20

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = "2e6f31d4aa10"
down_revision: Union[str, None] = "9a2f4a2c5d91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns expected by current multi-tenant models.
    op.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS user_id VARCHAR(36)"))
    op.execute(text("ALTER TABLE agent_tasks ADD COLUMN IF NOT EXISTS user_id VARCHAR(36)"))

    # Indexes used by dashboard/jobs/agent status filters.
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_jobs_user_id ON jobs (user_id)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_agent_tasks_user_id ON agent_tasks (user_id)"))

    # Backfill jobs.user_id from applications where possible.
    op.execute(
        text(
            """
            UPDATE jobs j
            SET user_id = src.user_id
            FROM (
                SELECT job_id, MIN(user_id) AS user_id
                FROM applications
                WHERE user_id IS NOT NULL
                GROUP BY job_id
            ) AS src
            WHERE j.id = src.job_id
              AND j.user_id IS NULL
            """
        )
    )

    # Backfill agent_tasks.user_id from related application/job links if available.
    op.execute(
        text(
            """
            UPDATE agent_tasks t
            SET user_id = a.user_id
            FROM applications a
            WHERE t.user_id IS NULL
              AND t.related_application_id IS NOT NULL
              AND t.related_application_id = a.id
            """
        )
    )
    op.execute(
        text(
            """
            UPDATE agent_tasks t
            SET user_id = j.user_id
            FROM jobs j
            WHERE t.user_id IS NULL
              AND t.related_job_id IS NOT NULL
              AND t.related_job_id = j.id
              AND j.user_id IS NOT NULL
            """
        )
    )


def downgrade() -> None:
    op.execute(text("DROP INDEX IF EXISTS ix_agent_tasks_user_id"))
    op.execute(text("DROP INDEX IF EXISTS ix_jobs_user_id"))
    op.execute(text("ALTER TABLE agent_tasks DROP COLUMN IF EXISTS user_id"))
    op.execute(text("ALTER TABLE jobs DROP COLUMN IF EXISTS user_id"))
