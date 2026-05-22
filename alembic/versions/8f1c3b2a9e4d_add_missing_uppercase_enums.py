"""Add missing uppercase enum values

Revision ID: 8f1c3b2a9e4d
Revises: f9a5c2b3d1e6
Create Date: 2026-05-22 13:25:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '8f1c3b2a9e4d'
down_revision = 'f9a5c2b3d1e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add uppercase enum values that might be missing
    op.execute("""
    ALTER TYPE experiencelevel ADD VALUE IF NOT EXISTS 'ENTRY';
    ALTER TYPE experiencelevel ADD VALUE IF NOT EXISTS 'MID';
    ALTER TYPE experiencelevel ADD VALUE IF NOT EXISTS 'SENIOR';
    ALTER TYPE experiencelevel ADD VALUE IF NOT EXISTS 'LEAD';
    ALTER TYPE experiencelevel ADD VALUE IF NOT EXISTS 'UNKNOWN';
    ALTER TYPE experiencelevel ADD VALUE IF NOT EXISTS 'EXECUTIVE';
    """)
    
    op.execute("""
    ALTER TYPE jobsource ADD VALUE IF NOT EXISTS 'LINKEDIN';
    ALTER TYPE jobsource ADD VALUE IF NOT EXISTS 'INDEED';
    ALTER TYPE jobsource ADD VALUE IF NOT EXISTS 'INTERNSHALA';
    ALTER TYPE jobsource ADD VALUE IF NOT EXISTS 'REMOTEOK';
    ALTER TYPE jobsource ADD VALUE IF NOT EXISTS 'WELLFOUND';
    """)


def downgrade() -> None:
    # PostgreSQL enums cannot be easily downgraded (no REMOVE VALUE)
    # This is a best-effort downgrade - manual intervention may be needed
    pass
