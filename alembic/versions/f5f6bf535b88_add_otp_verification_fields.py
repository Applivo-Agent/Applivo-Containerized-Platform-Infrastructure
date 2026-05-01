"""add otp verification fields

Revision ID: f5f6bf535b88
Revises: c7dc8fa94484
Create Date: 2026-04-18 12:58:20.324223

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5f6bf535b88'
down_revision: Union[str, None] = 'c7dc8fa94484'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to users table
    # Using server_default='0' for Boolean is_verified to ensure existing users are handled safely in SQLite
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'verified_at')
    op.drop_column('users', 'is_verified')
