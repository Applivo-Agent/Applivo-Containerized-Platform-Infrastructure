"""add fingerprint to platform_cookies

Revision ID: 653bbbcbe132
Revises: h2i3j4k5l6m7
Create Date: 2026-06-19 20:38:06.145816

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '653bbbcbe132'
down_revision: Union[str, None] = 'h2i3j4k5l6m7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add JSON fingerprint column to platform_cookies so the apply bot can
    # reuse the exact browser fingerprint that captured the session cookies.
    op.add_column('platform_cookies', sa.Column('fingerprint', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('platform_cookies', 'fingerprint')
