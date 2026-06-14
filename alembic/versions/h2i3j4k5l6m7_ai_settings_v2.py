"""AI Settings V2: add groq to aiprovider, add fallback columns

Revision ID: h2i3j4k5l6m7
Revises: g1h2i3j4k5l6
Create Date: 2026-06-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = "h2i3j4k5l6m7"
down_revision = "g1h2i3j4k5l6"
branch_labels = None
depends_on = None


def upgrade():
    # PostgreSQL requires enum value additions to be committed before use.
    # Run ALTER TYPE outside the current transaction via AUTOCOMMIT connection.
    conn = op.get_bind()
    conn.execute(text("COMMIT"))
    conn.execute(text("ALTER TYPE aiprovider ADD VALUE IF NOT EXISTS 'groq'"))
    conn.execute(text("BEGIN"))

    # Create fallbackstrategy enum (safe: only if it doesn't already exist)
    op.execute(text("""
        DO $$ BEGIN
            CREATE TYPE fallbackstrategy AS ENUM ('fastest', 'balanced', 'best_quality');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
    """))

    # Add fallback columns to user_settings
    op.execute(text("""
        ALTER TABLE user_settings
        ADD COLUMN IF NOT EXISTS fallback_enabled BOOLEAN NOT NULL DEFAULT true,
        ADD COLUMN IF NOT EXISTS fallback_strategy fallbackstrategy NOT NULL DEFAULT 'balanced'
    """))

    # Now safe to use the new enum value
    op.execute(text("""
        UPDATE user_settings SET ai_provider = 'groq', ai_model = 'auto'
        WHERE ai_provider IN ('openai', 'anthropic')
    """))

    # Add tracking columns to ai_usage_logs
    op.execute(text("""
        ALTER TABLE ai_usage_logs
        ADD COLUMN IF NOT EXISTS fallback_triggered BOOLEAN NOT NULL DEFAULT false,
        ADD COLUMN IF NOT EXISTS estimated_cost_usd FLOAT DEFAULT 0
    """))


def downgrade():
    op.execute(text("ALTER TABLE user_settings DROP COLUMN IF EXISTS fallback_strategy"))
    op.execute(text("ALTER TABLE user_settings DROP COLUMN IF EXISTS fallback_enabled"))
    op.execute(text("DROP TYPE IF EXISTS fallbackstrategy"))
    op.execute(text("ALTER TABLE ai_usage_logs DROP COLUMN IF EXISTS fallback_triggered"))
    op.execute(text("ALTER TABLE ai_usage_logs DROP COLUMN IF EXISTS estimated_cost_usd"))
