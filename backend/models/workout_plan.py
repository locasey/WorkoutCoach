from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Base


class WorkoutPlan(Base):
    __tablename__ = 'workout_plans'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=True)  # Nullable for MVP (single user)
    goal = Column(Text, nullable=False)
    duration_weeks = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=True)  # When the plan starts
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=False, nullable=False)
    user_request = Column(Text, nullable=True)  # Original chat request
    plan_data = Column(JSONB, nullable=True)  # Full plan JSON for reference
    
    # Relationship to workouts
    workouts = relationship("Workout", back_populates="workout_plan", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'goal': self.goal,
            'duration_weeks': self.duration_weeks,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'user_request': self.user_request,
            'plan_data': self.plan_data
        }

