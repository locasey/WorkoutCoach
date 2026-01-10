from sqlalchemy import Column, Integer, Float, String, Date, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Base


class Workout(Base):
    __tablename__ = 'workouts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_plan_id = Column(UUID(as_uuid=True), ForeignKey('workout_plans.id'), nullable=False)
    week = Column(Integer, nullable=False)  # 1-based week number
    day = Column(Integer, nullable=False)  # 1-7, where 1=Monday
    type = Column(String(50), nullable=False)  # long_run, tempo, intervals, easy_run, rest, cross_training
    distance_km = Column(Float, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    pace = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    scheduled_date = Column(Date, nullable=True)  # Calculated from plan start_date + week/day
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to workout plan
    workout_plan = relationship("WorkoutPlan", back_populates="workouts")
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
            'workout_plan_id': str(self.workout_plan_id),
            'week': self.week,
            'day': self.day,
            'type': self.type,
            'distance_km': self.distance_km,
            'duration_minutes': self.duration_minutes,
            'pace': self.pace,
            'notes': self.notes,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

