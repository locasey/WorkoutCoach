from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Base


class StravaSession(Base):
    """Store Strava OAuth tokens securely on the server side"""
    __tablename__ = 'strava_sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    session_token = Column(String(64), nullable=False, unique=True, index=True)  # Our session ID
    access_token = Column(Text, nullable=False)  # Encrypted in production
    refresh_token = Column(Text, nullable=True)  # For token refresh
    token_type = Column(String(50), default='Bearer')
    expires_at = Column(DateTime(timezone=True), nullable=True)
    athlete_id = Column(String(50), nullable=True)  # Strava athlete ID
    athlete_firstname = Column(String(100), nullable=True)
    athlete_lastname = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        """Convert model to dictionary (excludes sensitive tokens)"""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'session_token': self.session_token,
            'athlete_id': self.athlete_id,
            'athlete_firstname': self.athlete_firstname,
            'athlete_lastname': self.athlete_lastname,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def is_expired(self):
        """Check if the access token has expired"""
        from datetime import datetime, timezone
        if not self.expires_at:
            return True
        return datetime.now(timezone.utc) >= self.expires_at
