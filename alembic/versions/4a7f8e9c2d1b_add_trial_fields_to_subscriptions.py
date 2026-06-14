"""Add trial fields to subscriptions

Revision ID: 4a7f8e9c2d1b
Revises: f9a5c2b3d1e6
Create Date: 2026-05-22 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4a7f8e9c2d1b'
down_revision = 'f9a5c2b3d1e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new enum values for TRIAL and TRIAL_EXPIRED
    # NOTE: Some deployments use VARCHAR instead of native ENUM, so we guard the ALTER.
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT 1 FROM pg_type WHERE typname = 'subscriptionstatus'
    """))
    if result.scalar() is not None:
        op.execute("ALTER TYPE subscriptionstatus ADD VALUE IF NOT EXISTS 'TRIAL'")
        op.execute("ALTER TYPE subscriptionstatus ADD VALUE IF NOT EXISTS 'TRIAL_EXPIRED'")
    
    # Add is_trial column
    op.add_column('subscriptions', sa.Column('is_trial', sa.Boolean(), nullable=False, server_default=sa.false()))
    
    # Add trial_end_date column
    op.add_column('subscriptions', sa.Column('trial_end_date', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove trial_end_date column
    op.drop_column('subscriptions', 'trial_end_date')
    
    # Remove is_trial column
    op.drop_column('subscriptions', 'is_trial')
    
    # Note: We cannot remove enum values from PostgreSQL enums once added,
    # so TRIAL and TRIAL_EXPIRED will remain in the enum type.
