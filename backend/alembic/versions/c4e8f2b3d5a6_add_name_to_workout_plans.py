"""Add name column to workout_plans table

Revision ID: c4e8f2b3d5a6
Revises: f7g8h9i0j1k2
Create Date: 2026-02-01

This migration adds a `name` column to the workout_plans table for user-friendly
plan identification. Existing plans are backfilled with a name derived from their
goal (first 50 chars) or a default "Plan - <date>" format.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c4e8f2b3d5a6'
down_revision = 'f7g8h9i0j1k2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add name column (nullable initially for backfill)
    op.add_column('workout_plans', sa.Column('name', sa.String(255), nullable=True))

    # Backfill existing plans: use first 50 chars of goal, or default name
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE workout_plans
        SET name = CASE
            WHEN goal IS NOT NULL AND LENGTH(goal) > 0
            THEN LEFT(goal, 50)
            ELSE 'Plan - ' || TO_CHAR(created_at, 'Mon YYYY')
        END
        WHERE name IS NULL
    """))


def downgrade() -> None:
    op.drop_column('workout_plans', 'name')
