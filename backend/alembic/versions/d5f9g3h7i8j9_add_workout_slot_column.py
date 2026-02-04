"""Add slot column to workouts table for multiple workouts per day (LOC-22)

Revision ID: d5f9g3h7i8j9
Revises: c4e8f2b3d5a6
Create Date: 2026-02-04

This migration adds a `slot` column to the workouts table to support up to 2 workouts
per day. The slot values are:
  - NULL: Single workout for the day (default, backward compatible)
  - 1: AM/first workout slot
  - 2: PM/second workout slot

Existing workouts remain with slot=NULL, which displays as a single workout.
When a second workout is added to a day, the existing one gets slot=1 and new gets slot=2.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd5f9g3h7i8j9'
down_revision = 'c4e8f2b3d5a6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add slot column (nullable for backward compatibility)
    # NULL = single workout, 1 = AM/first, 2 = PM/second
    op.add_column('workouts', sa.Column('slot', sa.Integer(), nullable=True))

    # Add check constraint to ensure slot is 1, 2, or NULL
    op.create_check_constraint(
        'ck_workouts_slot_range',
        'workouts',
        'slot IS NULL OR slot IN (1, 2)'
    )


def downgrade() -> None:
    # Remove check constraint first
    op.drop_constraint('ck_workouts_slot_range', 'workouts', type_='check')
    # Remove slot column
    op.drop_column('workouts', 'slot')
