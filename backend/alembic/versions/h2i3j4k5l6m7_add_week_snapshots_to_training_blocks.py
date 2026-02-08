"""Add week_snapshots column to training_blocks

Revision ID: h2i3j4k5l6m7
Revises: g1h2i3j4k5l6
Create Date: 2026-02-08

Adds week_snapshots JSONB column to training_blocks for storing
regeneration history per week (up to 3 snapshots per week, FIFO).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'h2i3j4k5l6m7'
down_revision = 'g1h2i3j4k5l6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('training_blocks', sa.Column('week_snapshots', JSONB(), nullable=True, server_default='{}'))


def downgrade() -> None:
    op.drop_column('training_blocks', 'week_snapshots')
