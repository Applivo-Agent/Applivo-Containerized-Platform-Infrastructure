"""add ai_provider to job_analyses

Revision ID: 1f4e5c7a9b12
Revises: c7dc8fa94484
Create Date: 2026-04-19 19:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f4e5c7a9b12'
down_revision: Union[str, None] = 'c7dc8fa94484'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('job_analyses', sa.Column('ai_provider', sa.String(length=20), nullable=True))
    op.create_index(op.f('ix_job_analyses_ai_provider'), 'job_analyses', ['ai_provider'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_job_analyses_ai_provider'), table_name='job_analyses')
    op.drop_column('job_analyses', 'ai_provider')
