"""
Invite Code Service for Workout Coach

Manages beta access invite codes - generation, validation, and redemption.
"""

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.invite_code import InviteCode

# Default expiry: 5 days
INVITE_CODE_EXPIRY_DAYS = 5


class InviteCodeService:

    @staticmethod
    def generate_code(db: Session, created_by: uuid.UUID, expiry_days: int = INVITE_CODE_EXPIRY_DAYS) -> InviteCode:
        """Generate a new invite code."""
        code = secrets.token_urlsafe(8).upper()[:10]  # 10-char alphanumeric
        expires_at = datetime.now(timezone.utc) + timedelta(days=expiry_days)

        invite = InviteCode(
            code=code,
            created_by=created_by,
            expires_at=expires_at
        )
        db.add(invite)
        db.commit()
        db.refresh(invite)
        return invite

    @staticmethod
    def validate_and_use(db: Session, code: str, user_id: uuid.UUID) -> InviteCode | None:
        """
        Validate an invite code and mark it as used. Atomic with row lock.

        Returns the InviteCode if valid, None if invalid/expired/used.
        """
        now = datetime.now(timezone.utc)

        # Row-level lock to prevent race conditions
        invite = db.query(InviteCode).filter(
            and_(
                InviteCode.code == code,
                InviteCode.is_used == False,
                InviteCode.expires_at > now
            )
        ).with_for_update().first()

        if not invite:
            return None

        invite.is_used = True
        invite.used_by = user_id
        db.commit()
        db.refresh(invite)
        return invite

    @staticmethod
    def get_all_codes(db: Session) -> list[InviteCode]:
        """Get all invite codes, ordered by creation date."""
        return db.query(InviteCode).order_by(InviteCode.created_at.desc()).all()

    @staticmethod
    def get_code_by_value(db: Session, code: str) -> InviteCode | None:
        """Look up a code by its string value."""
        return db.query(InviteCode).filter(InviteCode.code == code).first()
