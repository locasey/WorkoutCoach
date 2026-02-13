from sqlalchemy import Column, Float, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Base


class StravaActivity(Base):
    __tablename__ = 'strava_activities'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    strava_id = Column(String(50), nullable=False, unique=True)  # Strava's activity ID
    name = Column(String(255), nullable=False)
    activity_type = Column(String(50), nullable=False)  # Run, Ride, Swim, etc.
    distance_km = Column(Float, nullable=True)
    moving_time_minutes = Column(Float, nullable=True)
    elapsed_time_minutes = Column(Float, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    average_speed_kmh = Column(Float, nullable=True)
    average_heartrate = Column(Float, nullable=True)
    max_heartrate = Column(Float, nullable=True)
    total_elevation_gain = Column(Float, nullable=True)

    # Link to workout (optional - for matching activities to planned workouts)
    linked_workout_id = Column(UUID(as_uuid=True), ForeignKey('workouts.id'), nullable=True)
    linked_workout = relationship("Workout", backref="strava_activities")

    # Metadata
    imported_at = Column(DateTime(timezone=True), server_default=func.now())
    raw_data = Column(Text, nullable=True)  # Store original Strava response as JSON string

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'strava_id': self.strava_id,
            'name': self.name,
            'activity_type': self.activity_type,
            'distance_km': self.distance_km,
            'moving_time_minutes': self.moving_time_minutes,
            'elapsed_time_minutes': self.elapsed_time_minutes,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'average_speed_kmh': self.average_speed_kmh,
            'average_heartrate': self.average_heartrate,
            'max_heartrate': self.max_heartrate,
            'total_elevation_gain': self.total_elevation_gain,
            'linked_workout_id': str(self.linked_workout_id) if self.linked_workout_id else None,
            'imported_at': self.imported_at.isoformat() if self.imported_at else None
        }
