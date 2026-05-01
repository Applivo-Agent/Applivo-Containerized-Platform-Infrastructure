"""Add production tables: user_sessions, subscriptions, payments, platform_cookies, chat_usage, platform_messages, chat_messages

Revision ID: add_prod_tables_001
Revises: security_models_001
Create Date: 2026-04-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'add_prod_tables_001'
down_revision: Union[str, None] = 'security_models_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── user_sessions ──────────────────────────────────────────
    op.execute(text("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id VARCHAR(36) PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            device_id VARCHAR(255) NOT NULL,
            device_name VARCHAR(255),
            device_type VARCHAR(50),
            browser VARCHAR(100),
            os VARCHAR(100),
            ip_address VARCHAR(45),
            location VARCHAR(255),
            user_agent TEXT,
            refresh_token_hash VARCHAR(255),
            refresh_token_expires_at TIMESTAMPTZ,
            access_token_jti VARCHAR(255),
            last_used_at TIMESTAMPTZ,
            is_current BOOLEAN NOT NULL DEFAULT false,
            is_active BOOLEAN NOT NULL DEFAULT true,
            CONSTRAINT uq_user_device_session UNIQUE (user_id, device_id),
            CONSTRAINT fk_user_sessions_user_id FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """))

    # ── subscriptions ──────────────────────────────────────────
    op.execute(text("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id VARCHAR(36) PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            plan VARCHAR(20) NOT NULL,
            status VARCHAR(20) NOT NULL,
            start_date TIMESTAMPTZ NOT NULL,
            end_date TIMESTAMPTZ,
            razorpay_subscription_id VARCHAR(255),
            CONSTRAINT fk_subscriptions_user_id FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """))

    # ── payments ───────────────────────────────────────────────
    op.execute(text("""
        CREATE TABLE IF NOT EXISTS payments (
            id VARCHAR(36) PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            subscription_id VARCHAR(36),
            amount INTEGER NOT NULL,
            currency VARCHAR(10) NOT NULL DEFAULT 'INR',
            status VARCHAR(20) NOT NULL,
            razorpay_order_id VARCHAR(255),
            razorpay_payment_id VARCHAR(255),
            razorpay_signature VARCHAR(500),
            plan VARCHAR(50),
            CONSTRAINT fk_payments_user_id FOREIGN KEY (user_id) REFERENCES users(id),
            CONSTRAINT fk_payments_subscription_id FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
        )
    """))

    # ── platform_cookies ───────────────────────────────────────
    op.execute(text("""
        CREATE TABLE IF NOT EXISTS platform_cookies (
            id VARCHAR(36) PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            platform VARCHAR(50) NOT NULL,
            encrypted_cookies TEXT NOT NULL,
            is_valid BOOLEAN NOT NULL DEFAULT true,
            expires_at TIMESTAMPTZ,
            last_validated_at TIMESTAMPTZ,
            last_used_at TIMESTAMPTZ,
            CONSTRAINT fk_platform_cookies_user_id FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """))

    # NOTE:
    # chat_usage/chat_messages/platform_messages are created in the
    # cbbc170b5f44 migration branch. Do not create them here to avoid
    # duplicate DDL before merge revision c7dc8fa94484.


def downgrade() -> None:
    op.execute(text("DROP TABLE IF EXISTS platform_cookies"))
    op.execute(text("DROP TABLE IF EXISTS payments"))
    op.execute(text("DROP TABLE IF EXISTS subscriptions"))
    op.execute(text("DROP TABLE IF EXISTS user_sessions"))
    
    # Optional: drop enums if they are recreated every time, but usually better to leave them 
    # unless you are sure no other tables use them.
