from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Base

import enum


class UserRole(str, enum.Enum):
    super_admin = 'super_admin'
    admin = 'admin'
    beta_tester = 'beta_tester'


user_role_enum = Enum(
    'super_admin', 'admin', 'beta_tester',
    name='user_role',
    create_type=False
)


class User(Base):
    """
    Represents an authenticated user.

    Users are created via Google OAuth + invite code (beta access).
    The seed super_admin user is created in migration and linked on first Google login.
    """
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=True)
    google_id = Column(String(255), nullable=False, unique=True, index=True)
    role = Column(user_role_enum, nullable=False, default='beta_tester')
    preferences = Column(JSONB, nullable=True, default=dict)
    settings = Column(JSONB, nullable=True, default=dict)
    invite_code_used = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'preferences': self.preferences,
            'settings': self.settings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
