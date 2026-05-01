"""merge multiple heads

Revision ID: c7dc8fa94484
Revises: add_prod_tables_001, cbbc170b5f44
Create Date: 2026-04-18 12:57:15.204943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7dc8fa94484'
down_revision: Union[str, None] = ('add_prod_tables_001', 'cbbc170b5f44')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
