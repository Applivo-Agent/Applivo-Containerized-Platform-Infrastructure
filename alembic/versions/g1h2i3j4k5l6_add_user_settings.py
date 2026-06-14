"""Add user_settings and settings_audit_logs tables

Revision ID: g1h2i3j4k5l6
Revises: security_models_001
Create Date: 2026-06-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = "g1h2i3j4k5l6"
down_revision = ("4a7f8e9c2d1b", "8f1c3b2a9e4d", "e1c2d3f4a5b6", "d636b3a582f7", "a1b2c3d4e5f6")
branch_labels = None
depends_on = None


def upgrade():
    # Enums
    op.execute(text("CREATE TYPE agentmode AS ENUM ('manual', 'semi_auto', 'full_auto')"))
    op.execute(text("CREATE TYPE agentstrategy AS ENUM ('aggressive', 'balanced', 'quality')"))
    op.execute(text("CREATE TYPE scheduleinterval AS ENUM ('30min', '1hour', '6hours', 'daily')"))
    op.execute(text("CREATE TYPE aiprovider AS ENUM ('openai', 'anthropic', 'gemini', 'openrouter')"))
    op.execute(text("CREATE TYPE reasoningdepth AS ENUM ('fast', 'balanced', 'deep')"))
    op.execute(text("CREATE TYPE appgenstyle AS ENUM ('professional', 'technical', 'startup', 'enterprise')"))
    op.execute(text("CREATE TYPE notificationfrequency AS ENUM ('instant', 'hourly', 'daily')"))
    op.execute(text("CREATE TYPE dashboardlayout AS ENUM ('compact', 'comfortable', 'spacious')"))

    op.execute(text("""
        CREATE TABLE IF NOT EXISTS user_settings (
            id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

            user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT uq_user_settings_user UNIQUE (user_id),

            -- General
            timezone VARCHAR(50) NOT NULL DEFAULT 'Asia/Kolkata',
            language VARCHAR(10) NOT NULL DEFAULT 'en',
            date_format VARCHAR(20) NOT NULL DEFAULT 'DD/MM/YYYY',
            theme VARCHAR(10) NOT NULL DEFAULT 'dark',
            dashboard_layout dashboardlayout NOT NULL DEFAULT 'comfortable',

            -- Notifications (JSON)
            notification_channels JSONB NOT NULL DEFAULT '{"email": true, "telegram": false, "discord": false, "slack": false}',
            notification_types JSONB NOT NULL DEFAULT '{"jobs_found": true, "application_submitted": true, "interview_invitation": true, "resume_analysis_completed": false, "weekly_summary": true, "ai_agent_alerts": true, "workflow_failures": true}',
            notification_frequency notificationfrequency NOT NULL DEFAULT 'instant',
            telegram_chat_id VARCHAR(50),
            notification_email VARCHAR(255),

            -- Job Automation
            agent_mode agentmode NOT NULL DEFAULT 'manual',
            auto_scrape_jobs BOOLEAN NOT NULL DEFAULT true,
            auto_analyze_jobs BOOLEAN NOT NULL DEFAULT true,
            auto_queue_jobs BOOLEAN NOT NULL DEFAULT false,
            auto_apply BOOLEAN NOT NULL DEFAULT false,
            daily_application_limit INTEGER NOT NULL DEFAULT 10,
            weekly_application_limit INTEGER NOT NULL DEFAULT 50,
            require_manual_approval BOOLEAN NOT NULL DEFAULT true,
            auto_approval_threshold INTEGER NOT NULL DEFAULT 75,
            schedule_interval scheduleinterval NOT NULL DEFAULT '6hours',
            next_scheduled_run TIMESTAMP WITH TIME ZONE,

            -- Agent Strategy
            agent_strategy agentstrategy NOT NULL DEFAULT 'balanced',

            -- AI Settings
            ai_provider aiprovider NOT NULL DEFAULT 'openai',
            ai_model VARCHAR(50) NOT NULL DEFAULT 'gpt-4o',
            reasoning_depth reasoningdepth NOT NULL DEFAULT 'balanced',
            app_gen_style appgenstyle NOT NULL DEFAULT 'professional',

            -- Platform Connections (JSON)
            platform_connections JSONB NOT NULL DEFAULT '{"linkedin": {"connected": false, "last_sync": null, "health": "disconnected"}, "internshala": {"connected": false, "last_sync": null, "health": "disconnected"}, "indeed": {"connected": false, "last_sync": null, "health": "disconnected"}, "naukri": {"connected": false, "last_sync": null, "health": "disconnected"}}',

            -- Security
            two_factor_enabled BOOLEAN NOT NULL DEFAULT false,
            two_factor_secret VARCHAR(255),
            api_keys JSONB,
            webhooks JSONB,

            -- Advanced
            debug_mode BOOLEAN NOT NULL DEFAULT false,
            experimental_features BOOLEAN NOT NULL DEFAULT false
        )
    """))

    op.execute(text("CREATE INDEX ix_user_settings_user_id ON user_settings(user_id)"))

    op.execute(text("""
        CREATE TABLE IF NOT EXISTS settings_audit_logs (
            id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

            user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            setting_key VARCHAR(100) NOT NULL,
            old_value TEXT,
            new_value TEXT,
            ip_address VARCHAR(45),
            user_agent TEXT,
            source VARCHAR(20) NOT NULL DEFAULT 'web'
        )
    """))

    op.execute(text("CREATE INDEX ix_audit_user_id ON settings_audit_logs(user_id)"))
    op.execute(text("CREATE INDEX ix_audit_setting_key ON settings_audit_logs(setting_key)"))
    op.execute(text("CREATE INDEX ix_audit_created_at ON settings_audit_logs(created_at)"))


def downgrade():
    op.execute(text("DROP TABLE IF EXISTS settings_audit_logs"))
    op.execute(text("DROP TABLE IF EXISTS user_settings"))
    op.execute(text("DROP TYPE IF EXISTS dashboardlayout"))
    op.execute(text("DROP TYPE IF EXISTS notificationfrequency"))
    op.execute(text("DROP TYPE IF EXISTS appgenstyle"))
    op.execute(text("DROP TYPE IF EXISTS reasoningdepth"))
    op.execute(text("DROP TYPE IF EXISTS aiprovider"))
    op.execute(text("DROP TYPE IF EXISTS scheduleinterval"))
    op.execute(text("DROP TYPE IF EXISTS agentstrategy"))
    op.execute(text("DROP TYPE IF EXISTS agentmode"))
