"""add missing user auth columns

Revision ID: 9a2f4a2c5d91
Revises: f5f6bf535b88, 1f4e5c7a9b12
Create Date: 2026-04-20

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '9a2f4a2c5d91'
down_revision: Union[str, Sequence[str], None] = ('f5f6bf535b88', '1f4e5c7a9b12')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure auth columns expected by app.models.user.User exist on production DBs.
    op.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(255)"))
    op.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT false"))
    op.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS verified_at TIMESTAMPTZ"))
    op.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255)"))
    op.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_expires_at TIMESTAMPTZ"))

    op.execute(
        text(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_enum e
                    JOIN pg_type t ON t.oid = e.enumtypid
                    WHERE t.typname = 'experiencelevel' AND e.enumlabel = 'ENTRY'
                ) THEN
                    ALTER TYPE experiencelevel RENAME VALUE 'ENTRY' TO 'entry';
                END IF;

                IF EXISTS (
                    SELECT 1 FROM pg_enum e
                    JOIN pg_type t ON t.oid = e.enumtypid
                    WHERE t.typname = 'experiencelevel' AND e.enumlabel = 'MID'
                ) THEN
                    ALTER TYPE experiencelevel RENAME VALUE 'MID' TO 'mid';
                END IF;

                IF EXISTS (
                    SELECT 1 FROM pg_enum e
                    JOIN pg_type t ON t.oid = e.enumtypid
                    WHERE t.typname = 'experiencelevel' AND e.enumlabel = 'SENIOR'
                ) THEN
                    ALTER TYPE experiencelevel RENAME VALUE 'SENIOR' TO 'senior';
                END IF;

                IF EXISTS (
                    SELECT 1 FROM pg_enum e
                    JOIN pg_type t ON t.oid = e.enumtypid
                    WHERE t.typname = 'experiencelevel' AND e.enumlabel = 'LEAD'
                ) THEN
                    ALTER TYPE experiencelevel RENAME VALUE 'LEAD' TO 'lead';
                END IF;

                IF EXISTS (
                    SELECT 1 FROM pg_enum e
                    JOIN pg_type t ON t.oid = e.enumtypid
                    WHERE t.typname = 'experiencelevel' AND e.enumlabel = 'UNKNOWN'
                ) THEN
                    ALTER TYPE experiencelevel RENAME VALUE 'UNKNOWN' TO 'unknown';
                END IF;

                ALTER TYPE experiencelevel ADD VALUE IF NOT EXISTS 'executive';
            END
            $$;
            """
        )
    )

    op.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_google_id ON users (google_id)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_users_password_reset_token ON users (password_reset_token)"))


def downgrade() -> None:
    op.execute(text("DROP INDEX IF EXISTS ix_users_password_reset_token"))
    op.execute(text("DROP INDEX IF EXISTS ix_users_google_id"))

    op.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS password_reset_expires_at"))
    op.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS password_reset_token"))
    op.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS verified_at"))
    op.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS is_verified"))
    op.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS google_id"))
