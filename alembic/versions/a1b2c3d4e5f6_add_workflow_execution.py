"""Add workflow execution tables

Revision ID: a1b2c3d4e5f6
Revises: f5f6bf535b88
Create Date: 2026-06-04 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f5f6bf535b88'
branch_labels = None
depends_on = None


def _create_enum_if_not_exists(name: str, values: list[str]) -> None:
    """Idempotent enum creation for PostgreSQL."""
    values_sql = ", ".join(f"'{v}'" for v in values)
    op.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{name}') THEN
                CREATE TYPE {name} AS ENUM ({values_sql});
            END IF;
        END$$;
        """
    )


def upgrade() -> None:
    # Create enum types idempotently
    _create_enum_if_not_exists("workflowstatus", ["PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED"])
    _create_enum_if_not_exists("workflowsteptype", ["SCRAPE", "ANALYZE", "QUEUE", "DEPLOY"])
    _create_enum_if_not_exists("workflowstepstatus", ["PENDING", "RUNNING", "COMPLETED", "FAILED", "SKIPPED"])

    workflowstatus_enum = postgresql.ENUM(
        'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED',
        name='workflowstatus', create_type=False,
    )
    workflowsteptype_enum = postgresql.ENUM(
        'SCRAPE', 'ANALYZE', 'QUEUE', 'DEPLOY',
        name='workflowsteptype', create_type=False,
    )
    workflowstepstatus_enum = postgresql.ENUM(
        'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'SKIPPED',
        name='workflowstepstatus', create_type=False,
    )

    # workflow_executions table
    op.create_table(
        'workflow_executions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('status', workflowstatus_enum, nullable=False, index=True),
        sa.Column('current_step_index', sa.Integer, nullable=False, default=0),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('result_summary', postgresql.JSONB, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # workflow_steps table
    op.create_table(
        'workflow_steps',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_id', sa.String(36), sa.ForeignKey('workflow_executions.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('step_index', sa.Integer, nullable=False),
        sa.Column('step_type', workflowsteptype_enum, nullable=False),
        sa.Column('status', workflowstepstatus_enum, nullable=False, index=True, server_default='PENDING'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('result_summary', postgresql.JSONB, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('tokens_used', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('workflow_steps')
    op.drop_table('workflow_executions')
    op.execute("DROP TYPE IF EXISTS workflowstepstatus")
    op.execute("DROP TYPE IF EXISTS workflowsteptype")
    op.execute("DROP TYPE IF EXISTS workflowstatus")
