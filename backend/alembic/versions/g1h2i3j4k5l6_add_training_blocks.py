"""Add training_blocks table and update workouts for new architecture

Revision ID: g1h2i3j4k5l6
Revises: d5f9g3h7i8j9
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
down_revision = 'd5f9g3h7i8j9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum and table using raw SQL to avoid SQLAlchemy enum issues
    op.execute("""
        CREATE TYPE training_block_status AS ENUM ('active', 'completed', 'abandoned');

        CREATE TABLE training_blocks (
            id UUID PRIMARY KEY,
            user_id INTEGER,
            event_name VARCHAR(255) NOT NULL,
            event_distance VARCHAR(50) NOT NULL,
            target_date DATE NOT NULL,
            start_date DATE NOT NULL,
            total_weeks INTEGER NOT NULL,
            phase_map JSONB NOT NULL,
            status training_block_status NOT NULL DEFAULT 'active',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        );
    """)

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
