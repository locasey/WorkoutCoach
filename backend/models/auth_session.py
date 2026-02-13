from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Base


class AuthSession(Base):
    """Store authentication session tokens persistently"""
    __tablename__ = 'auth_sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    session_token = Column(String(64), nullable=False, unique=True, index=True)  # Session token for auth
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)  # When session expires
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'session_token': self.session_token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def is_expired(self):
        """Check if the session has expired"""
        from datetime import datetime, timezone
        if not self.expires_at:
            return True
        return datetime.now(timezone.utc) >= self.expires_at
