"""normalize enum-like strings to uppercase

Revision ID: f9a5c2b3d1e6
Revises: c7dc8fa94484
Create Date: 2026-04-30 13:40:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'f9a5c2b3d1e6'
down_revision = 'c7dc8fa94484'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Normalize legacy lowercase values to the canonical uppercase enums.
    # Idempotent: only updates values where lower != upper.
    op.execute("""
    UPDATE jobs
    SET source = UPPER(source::text)::jobsource
    WHERE source IS NOT NULL AND source::text <> UPPER(source::text)
    """)

    op.execute("""
    UPDATE jobs
    SET experience_level = UPPER(experience_level::text)::experience_level
    WHERE experience_level IS NOT NULL AND experience_level::text <> UPPER(experience_level::text)
    """)

    op.execute("""
    UPDATE user_profiles
    SET experience_level = UPPER(experience_level::text)::experience_level
    WHERE experience_level IS NOT NULL AND experience_level::text <> UPPER(experience_level::text)
    """)


def downgrade() -> None:
    # Downgrade: revert values to lowercase to restore previous appearance.
    # This is reversible but best-effort; production systems may prefer keeping uppercase.
    op.execute("""
    UPDATE jobs
    SET source = LOWER(source::text)::jobsource
    WHERE source IS NOT NULL AND source::text <> LOWER(source::text)
    """)

    op.execute("""
    UPDATE jobs
    SET experience_level = LOWER(experience_level::text)::experience_level
    WHERE experience_level IS NOT NULL AND experience_level::text <> LOWER(experience_level::text)
    """)

    op.execute("""
    UPDATE user_profiles
    SET experience_level = LOWER(experience_level::text)::experience_level
    WHERE experience_level IS NOT NULL AND experience_level::text <> LOWER(experience_level::text)
    """)
