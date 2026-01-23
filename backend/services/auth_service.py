"""
Authentication Service for Workout Coach

Provides simple username/password authentication with session management.
Credentials are stored in environment variables for single-user MVP.
Sessions are stored persistently in PostgreSQL database.
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, g
from database import get_db
from models.auth_session import AuthSession

# Session expiration time (24 hours)
SESSION_EXPIRY_HOURS = 24


def _get_auth_credentials():
    """
    Get authentication credentials from environment variables.

    Returns:
        tuple: (username, password) or (None, None) if not configured
    """
    username = os.getenv('AUTH_USERNAME')
    password = os.getenv('AUTH_PASSWORD')
    return username, password


def _hash_password(password: str) -> str:
    """
    Hash a password for comparison.
    Uses SHA-256 for simple MVP authentication.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return hashlib.sha256(password.encode()).hexdigest()


def is_auth_enabled() -> bool:
    """
    Check if authentication is enabled (credentials are configured).

    Returns:
        bool: True if both AUTH_USERNAME and AUTH_PASSWORD are set
    """
    username, password = _get_auth_credentials()
    return bool(username and password)


def validate_credentials(username: str, password: str) -> bool:
    """
    Validate username and password against environment variables.

    Args:
        username: Provided username
        password: Provided password

    Returns:
        bool: True if credentials match
    """
    expected_username, expected_password = _get_auth_credentials()

    if not expected_username or not expected_password:
        return False

    # Use constant-time comparison to prevent timing attacks
    username_match = secrets.compare_digest(username, expected_username)
    password_match = secrets.compare_digest(password, expected_password)

    return username_match and password_match


def create_session() -> str:
    """
    Create a new session token and store it in the database.

    Returns:
        str: Generated session token
    """
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_EXPIRY_HOURS)

    db = next(get_db())
    try:
        session = AuthSession(
            session_token=token,
            expires_at=expires_at,
            user_id=None  # Nullable for MVP (single user)
        )
        db.add(session)
        db.commit()
        return token
    except Exception as e:
        db.rollback()
        raise  # Re-raise to be handled by caller
    finally:
        db.close()


def validate_session(token: str) -> bool:
    """
    Validate a session token from the database.
    Also performs on-demand cleanup of expired sessions.

    Args:
        token: Session token to validate

    Returns:
        bool: True if session is valid and not expired
    """
    if not token:
        return False

    db = next(get_db())
    try:
        now = datetime.now(timezone.utc)
        
        # Find session by token
        session = db.query(AuthSession).filter(
            AuthSession.session_token == token
        ).first()

        if not session:
            return False

        # Check if expired
        if now >= session.expires_at:
            # Clean up expired session (on-demand cleanup)
            db.delete(session)
            db.commit()
            return False

        return True
    except Exception:
        # Fail closed: if DB error, reject session
        db.rollback()
        return False
    finally:
        db.close()


def delete_session(token: str) -> bool:
    """
    Delete a session from the database (logout).

    Args:
        token: Session token to delete

    Returns:
        bool: True if session was deleted
    """
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


def get_session_token_from_request():
    """
    Extract session token from request headers or cookies.

    Checks in order:
    1. Authorization header (Bearer token)
    2. X-Auth-Session header
    3. auth_session cookie

    Returns:
        str or None: Session token if found
    """
    # Try Authorization header first (Bearer token)
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]

    # Try X-Auth-Session header
    session_header = request.headers.get('X-Auth-Session')
    if session_header:
        return session_header

    # Try cookie
    return request.cookies.get('auth_session')


def require_auth(f):
    """
    Decorator to require authentication for a route.

    If auth is not enabled (no credentials configured), allows request through.
    Otherwise, validates the session token.

    Usage:
        @app.route('/api/protected')
        @require_auth
        def protected_route():
            return jsonify({"message": "Protected data"})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip auth if not enabled (development without credentials)
        if not is_auth_enabled():
            return f(*args, **kwargs)

        token = get_session_token_from_request()

        if not token:
            return jsonify({
                "error": "Authentication required",
                "code": "AUTH_REQUIRED"
            }), 401

        if not validate_session(token):
            return jsonify({
                "error": "Invalid or expired session",
                "code": "INVALID_SESSION"
            }), 401

        # Store token in g for potential use in route
        g.auth_token = token

        return f(*args, **kwargs)

    return decorated_function


def cleanup_expired_sessions():
    """
    Remove all expired sessions from the database.
    Call periodically to prevent database buildup.
    Uses indexed query on expires_at for efficiency.

    Returns:
        int: Number of expired sessions deleted
    """
    db = next(get_db())
    try:
        now = datetime.now(timezone.utc)
        
        # Query expired sessions using indexed expires_at column
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
