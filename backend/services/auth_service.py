"""
Authentication Service for Workout Coach

Google OAuth authentication with session management.
Sessions are stored persistently in PostgreSQL database.
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, g
from database import get_db
from models.auth_session import AuthSession
from models.user import User

# Session expiration time (24 hours)
SESSION_EXPIRY_HOURS = 24


def validate_google_token(credential: str) -> dict:
    """
    Validate a Google OAuth id_token and return user info.

    Args:
        credential: The id_token from Google Sign-In

    Returns:
        dict with keys: google_id (sub), email, name

    Raises:
        ValueError: If token is invalid
    """
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests

    client_id = os.getenv('GOOGLE_CLIENT_ID')
    if not client_id:
        raise ValueError("GOOGLE_CLIENT_ID not configured")

    try:
        id_info = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            client_id
        )

        # Verify issuer
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError("Invalid token issuer")

        return {
            'google_id': id_info['sub'],
            'email': id_info.get('email', ''),
            'name': id_info.get('name', ''),
        }
    except Exception as e:
        raise ValueError(f"Invalid Google token: {str(e)}")


def create_session_for_user(db, user_id) -> str:
    """
    Create a new session token linked to a user.

    Args:
        db: Database session
        user_id: UUID of the user

    Returns:
        str: Generated session token
    """
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_EXPIRY_HOURS)

    session = AuthSession(
        session_token=token,
        expires_at=expires_at,
        user_id=user_id
    )
    db.add(session)
    db.commit()
    return token


def get_user_from_session(db, token: str) -> User | None:
    """
    Look up user from a session token.

    Returns User object if session is valid, None otherwise.
    """
    if not token:
        return None

    now = datetime.now(timezone.utc)
    session = db.query(AuthSession).filter(
        AuthSession.session_token == token
    ).first()

    if not session:
        return None

    if now >= session.expires_at:
        db.delete(session)
        db.commit()
        return None

    user = db.query(User).filter(User.id == session.user_id).first()
    return user


def get_session_token_from_request():
    """
    Extract session token from request headers or cookies.

    Checks in order:
    1. Authorization header (Bearer token)
    2. X-Auth-Session header
    3. auth_session cookie
    """
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]

    session_header = request.headers.get('X-Auth-Session')
    if session_header:
        return session_header

    return request.cookies.get('auth_session')


def delete_session(token: str) -> bool:
    """Delete a session from the database (logout)."""
    if not token:
        return False

    db = next(get_db())
    try:
        session = db.query(AuthSession).filter(
            AuthSession.session_token == token
        ).first()

        if session:
            db.delete(session)
            db.commit()
            return True
        return False
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()


def require_auth(f):
    """
    Decorator to require authentication for a route.

    Validates the session token, looks up the user, and stores in flask.g:
    - g.current_user: User object
    - g.current_user_id: UUID
    - g.db: Database session (reused by route handler)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Let CORS preflight requests through
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)

        token = get_session_token_from_request()

        if not token:
            return jsonify({
                "error": "Authentication required",
                "code": "AUTH_REQUIRED"
            }), 401

        db = next(get_db())
        try:
            user = get_user_from_session(db, token)
            if not user:
                db.close()
                return jsonify({
                    "error": "Invalid or expired session",
                    "code": "INVALID_SESSION"
                }), 401

            g.current_user = user
            g.current_user_id = user.id
            g.db = db
            g.auth_token = token

            return f(*args, **kwargs)
        except Exception:
            db.close()
            raise

    return decorated_function


def require_admin(f):
    """
    Decorator to require admin or super_admin role.
    Must be used after @require_auth.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = getattr(g, 'current_user', None)
        if not user or user.role not in ('admin', 'super_admin'):
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)

    return decorated_function


def cleanup_expired_sessions():
    """Remove all expired sessions from the database."""
    db = next(get_db())
    try:
        now = datetime.now(timezone.utc)
        expired_sessions = db.query(AuthSession).filter(
            AuthSession.expires_at <= now
        ).all()

        count = len(expired_sessions)
        for session in expired_sessions:
            db.delete(session)

        db.commit()
        return count
    except Exception:
        db.rollback()
        return 0
    finally:
        db.close()
