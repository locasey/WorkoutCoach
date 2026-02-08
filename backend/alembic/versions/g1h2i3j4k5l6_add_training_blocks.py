"""Add training_blocks table and update workouts for new architecture

Revision ID: g1h2i3j4k5l6
Revises: f7g8h9i0j1k2
Create Date: 2026-02-08

This migration introduces the TrainingBlock model for the new architecture:
- Creates training_blocks table with event info, phases, and status
- Adds training_block_id FK to workouts (nullable, for new architecture)
- Adds phase column to workouts ("base", "build", "peak", "taper")
- Adds actuals JSONB column to workouts for logging actual performance
- Makes workout_plan_id nullable (for backward compatibility during transition)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = 'g1h2i3j4k5l6'
down_revision = 'f7g8h9i0j1k2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create training_block_status enum
    training_block_status = sa.Enum('active', 'completed', 'abandoned', name='training_block_status')
    training_block_status.create(op.get_bind(), checkfirst=True)

    # Create training_blocks table
    op.create_table(
        'training_blocks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('event_name', sa.String(255), nullable=False),
        sa.Column('event_distance', sa.String(50), nullable=False),
        sa.Column('target_date', sa.Date(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('total_weeks', sa.Integer(), nullable=False),
        sa.Column('phase_map', JSONB(), nullable=False),
        sa.Column('status', training_block_status, nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Add training_block_id to workouts (nullable FK)
    op.add_column('workouts', sa.Column('training_block_id', UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_workouts_training_block_id',
        'workouts', 'training_blocks',
        ['training_block_id'], ['id'],
        ondelete='CASCADE'
    )

    # Add phase column to workouts
    op.add_column('workouts', sa.Column('phase', sa.String(20), nullable=True))
    op.create_check_constraint(
        'ck_workouts_phase_values',
        'workouts',
        "phase IS NULL OR phase IN ('base', 'build', 'peak', 'taper')"
    )

    # Add actuals JSONB column to workouts
    op.add_column('workouts', sa.Column('actuals', JSONB(), nullable=True))

    # Make workout_plan_id nullable (for new architecture workouts)
    op.alter_column('workouts', 'workout_plan_id', nullable=True)


def downgrade() -> None:
    # Revert workout_plan_id to non-nullable (may fail if NULL values exist)
    op.alter_column('workouts', 'workout_plan_id', nullable=False)

    # Remove actuals column
    op.drop_column('workouts', 'actuals')

    # Remove phase constraint and column
    op.drop_constraint('ck_workouts_phase_values', 'workouts', type_='check')
    op.drop_column('workouts', 'phase')

    # Remove training_block_id FK and column
    op.drop_constraint('fk_workouts_training_block_id', 'workouts', type_='foreignkey')
    op.drop_column('workouts', 'training_block_id')

    # Drop training_blocks table
    op.drop_table('training_blocks')

    # Drop enum type
    sa.Enum(name='training_block_status').drop(op.get_bind(), checkfirst=True)
