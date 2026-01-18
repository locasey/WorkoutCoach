"""Add strava_activities and strava_sessions tables

Revision ID: a1b2c3d4e5f6
Revises: e3d14ef0a2bd
Create Date: 2026-01-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'e3d14ef0a2bd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create strava_sessions table
    op.create_table('strava_sessions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('session_token', sa.String(length=64), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_type', sa.String(length=50), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('athlete_id', sa.String(length=50), nullable=True),
        sa.Column('athlete_firstname', sa.String(length=100), nullable=True),
        sa.Column('athlete_lastname', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_strava_sessions_session_token', 'strava_sessions', ['session_token'], unique=True)

    # Create strava_activities table
    op.create_table('strava_activities',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('strava_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('distance_km', sa.Float(), nullable=True),
        sa.Column('moving_time_minutes', sa.Float(), nullable=True),
        sa.Column('elapsed_time_minutes', sa.Float(), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('average_speed_kmh', sa.Float(), nullable=True),
        sa.Column('average_heartrate', sa.Float(), nullable=True),
        sa.Column('max_heartrate', sa.Float(), nullable=True),
        sa.Column('total_elevation_gain', sa.Float(), nullable=True),
        sa.Column('linked_workout_id', sa.UUID(), nullable=True),
        sa.Column('imported_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('raw_data', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['linked_workout_id'], ['workouts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('strava_id')
    )


def downgrade() -> None:
    op.drop_table('strava_activities')
    op.drop_index('ix_strava_sessions_session_token', table_name='strava_sessions')
    op.drop_table('strava_sessions')
