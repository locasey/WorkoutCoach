from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Base


# Use PostgreSQL native enum (already created in migration)
training_block_status_enum = ENUM('active', 'completed', 'abandoned', name='training_block_status', create_type=False)


class TrainingBlock(Base):
    """
    Represents a training block for a specific race/event goal.

    A user can have at most one active TrainingBlock at a time.
    When no TrainingBlock exists (or none is active), user is in "maintenance mode".
    """
    __tablename__ = 'training_blocks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Event details
    event_name = Column(String(255), nullable=False)  # e.g., "Boston Marathon"
    event_distance = Column(String(50), nullable=False)  # "marathon", "half", "10k", "5k", or custom
    target_date = Column(Date, nullable=False)  # Race day

    # Plan structure
    start_date = Column(Date, nullable=False)  # When training begins
    total_weeks = Column(Integer, nullable=False)  # Total weeks in the block
    phase_map = Column(JSONB, nullable=False)  # {"base": [1,2,3,4], "build": [5,6,7,8], ...}
    week_snapshots = Column(JSONB, nullable=True, default={})  # Regeneration history per week

    # Status - uses PostgreSQL native enum
    status = Column(training_block_status_enum, default='active', nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to workouts
    workouts = relationship("Workout", back_populates="training_block", cascade="all, delete-orphan")

    def get_current_week(self):
        """Calculate current week number based on start_date and today."""
        from datetime import date
        if not self.start_date:
            return None
        days_elapsed = (date.today() - self.start_date).days
        if days_elapsed < 0:
            return 0  # Training hasn't started yet
        week = (days_elapsed // 7) + 1
        return min(week, self.total_weeks)

    def get_current_phase(self):
        """Get the phase name for the current week."""
        current_week = self.get_current_week()
        if not current_week or not self.phase_map:
            return None
        for phase_name, weeks in self.phase_map.items():
            if current_week in weeks:
                return phase_name
        return None

    def get_weeks_until_race(self):
        """Calculate weeks remaining until target_date."""
        from datetime import date
        if not self.target_date:
            return None
        days_remaining = (self.target_date - date.today()).days
        return max(0, days_remaining // 7)

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'event_name': self.event_name,
            'event_distance': self.event_distance,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'total_weeks': self.total_weeks,
            'phase_map': self.phase_map,
            'week_snapshots': self.week_snapshots,
            'status': self.status,
            'current_week': self.get_current_week(),
            'current_phase': self.get_current_phase(),
            'weeks_until_race': self.get_weeks_until_race(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
