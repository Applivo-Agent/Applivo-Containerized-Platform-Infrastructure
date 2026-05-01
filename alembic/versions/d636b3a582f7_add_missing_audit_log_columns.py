"""Add missing audit_log columns

Revision ID: d636b3a582f7
Revises: 2e6f31d4aa10
Create Date: 2026-04-22 21:03:30.763237

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd636b3a582f7'
down_revision: Union[str, None] = '2e6f31d4aa10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('audit_logs', sa.Column('request_method', sa.String(length=10), nullable=True))
    op.add_column('audit_logs', sa.Column('request_path', sa.String(length=500), nullable=True))
    op.add_column('audit_logs', sa.Column('request_id', sa.String(length=36), nullable=True))
    op.add_column('audit_logs', sa.Column('changes', sa.JSON(), nullable=True))
    op.add_column('audit_logs', sa.Column('error_code', sa.String(length=50), nullable=True))
    op.add_column('audit_logs', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))

def downgrade() -> None:
    op.drop_column('audit_logs', 'updated_at')
    op.drop_column('audit_logs', 'error_code')
    op.drop_column('audit_logs', 'changes')
    op.drop_column('audit_logs', 'request_id')
    op.drop_column('audit_logs', 'request_path')
    op.drop_column('audit_logs', 'request_method')
