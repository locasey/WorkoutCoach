"""Add users table, invite_codes table, convert user_id to UUID FK

Revision ID: p6a1b2c3d4e5
Revises: h2i3j4k5l6m7
Create Date: 2026-02-09

Phase 6a: Multi-user database foundation.
- Creates users table with role enum
- Creates invite_codes table
- Converts user_id from Integer nullable to UUID FK NOT NULL on all tables
- Adds user_id to workouts table (didn't have one)
- Seeds a super_admin user for the owner account
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid


# revision identifiers
revision = 'p6a1b2c3d4e5'
down_revision = 'h2i3j4k5l6m7'
branch_labels = None
depends_on = None

# Deterministic UUID for the seed user (so we can reference it in backfill)
OWNER_UUID = uuid.UUID('00000000-0000-4000-a000-000000000001')
OWNER_EMAIL = 'locasey615@gmail.com'


def upgrade() -> None:
    # --- Step 1: Create user_role enum and users table ---
    # Use raw SQL to avoid SQLAlchemy's before_create event trying to re-create the enum
    op.execute("""
        CREATE TYPE user_role AS ENUM ('super_admin', 'admin', 'beta_tester');

        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) NOT NULL UNIQUE,
            name VARCHAR(255),
            google_id VARCHAR(255) NOT NULL UNIQUE,
            role user_role NOT NULL DEFAULT 'beta_tester',
            preferences JSONB,
            settings JSONB,
            invite_code_used VARCHAR(50),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ
        );

        CREATE INDEX ix_users_email ON users (email);
        CREATE INDEX ix_users_google_id ON users (google_id);
    """)

    # --- Step 2: Seed super_admin user ---
    op.execute(
        f"""
        INSERT INTO users (id, email, name, google_id, role, created_at)
        VALUES (
            '{OWNER_UUID}',
            '{OWNER_EMAIL}',
            'Liam',
            'PENDING_GOOGLE_LINK',
            'super_admin',
            NOW()
        )
        """
    )

    # --- Step 3: Create invite_codes table ---
    op.create_table(
        'invite_codes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('code', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('used_by', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_used', sa.Boolean, default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Step 4: Convert user_id on existing tables ---
    # For each table: drop old Integer column, add UUID FK, backfill, set NOT NULL, add index

    for table_name in ['training_blocks', 'workout_plans', 'auth_sessions', 'strava_sessions', 'strava_activities']:
        # Drop old Integer user_id column (all values are NULL — no data loss)
        op.drop_column(table_name, 'user_id')

        # Add new UUID user_id column (nullable initially for backfill)
        op.add_column(table_name, sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True))

        # Backfill all existing rows to owner
        op.execute(f"UPDATE {table_name} SET user_id = '{OWNER_UUID}'")

        # Set NOT NULL
        op.alter_column(table_name, 'user_id', nullable=False)

        # Add index
        op.create_index(f'idx_{table_name}_user_id', table_name, ['user_id'])

    # --- Step 5: Add user_id to workouts table (doesn't have one yet) ---
    op.add_column('workouts', sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True))

    # Backfill from parent training_block or workout_plan
    op.execute(
        f"""
        UPDATE workouts w SET user_id = COALESCE(
            (SELECT tb.user_id FROM training_blocks tb WHERE tb.id = w.training_block_id),
            (SELECT wp.user_id FROM workout_plans wp WHERE wp.id = w.workout_plan_id),
            '{OWNER_UUID}'
        )
        """
    )

    # Set NOT NULL and add index
    op.alter_column('workouts', 'user_id', nullable=False)
    op.create_index('idx_workouts_user_id', 'workouts', ['user_id'])


def downgrade() -> None:
    # --- Reverse Step 5: Remove user_id from workouts ---
    op.drop_index('idx_workouts_user_id', table_name='workouts')
    op.drop_column('workouts', 'user_id')

    # --- Reverse Step 4: Convert user_id back to Integer nullable ---
    for table_name in ['strava_activities', 'strava_sessions', 'auth_sessions', 'workout_plans', 'training_blocks']:
        op.drop_index(f'idx_{table_name}_user_id', table_name=table_name)
        op.drop_column(table_name, 'user_id')
        op.add_column(table_name, sa.Column('user_id', sa.Integer, nullable=True))

    # --- Reverse Step 3: Drop invite_codes ---
    op.drop_table('invite_codes')

    # --- Reverse Step 2 & 1: Drop users and enum ---
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS user_role")
