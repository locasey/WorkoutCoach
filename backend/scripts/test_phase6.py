"""
Phase 6 E2E Tests — Multi-User Security & Preferences

Tests data isolation, user preferences CRUD, and session lifecycle.
Run against a live local server: python scripts/test_phase6.py

Requires: pip install requests
"""

import sys
import os
import uuid
import secrets
import requests
import json
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, SessionLocal
from models.user import User
from models.auth_session import AuthSession
from models.training_block import TrainingBlock
from models.workout import Workout

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

# Test tracking
passed = 0
failed = 0

def print_header(title):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}")

def pass_test(test_name, message=""):
    """Mark test as passed"""
    global passed
    passed += 1
    msg = f"{message}" if message else ""
    print(f"  ✓ {test_name} {msg}")

def fail_test(test_name, message=""):
    """Mark test as failed"""
    global failed
    failed += 1
    msg = f" - {message}" if message else ""
    print(f"  ✗ {test_name}{msg}")

def print_summary():
    """Print test summary"""
    total = passed + failed
    print(f"\n{'='*70}")
    print(f" Test Summary: {passed}/{total} passed")
    if failed > 0:
        print(f" {failed} test(s) failed")
    print(f"{'='*70}\n")

# ============================================================================
# Setup & Teardown
# ============================================================================

def setup_test_users():
    """
    Create 2 test users + sessions directly in DB.
    Returns: (token_a, token_b, user_a_id, user_b_id)
    """
    db = SessionLocal()
    try:
        # Create User A
        user_a_id = uuid.uuid4()
        user_a = User(
            id=user_a_id,
            email=f"test_a_{uuid.uuid4().hex[:8]}@example.com",
            name="Test User A",
            google_id=f"google_{uuid.uuid4().hex[:12]}",
            role='beta_tester',
            preferences=None,
            settings=None
        )
        db.add(user_a)

        # Create User B
        user_b_id = uuid.uuid4()
        user_b = User(
            id=user_b_id,
            email=f"test_b_{uuid.uuid4().hex[:8]}@example.com",
            name="Test User B",
            google_id=f"google_{uuid.uuid4().hex[:12]}",
            role='beta_tester',
            preferences=None,
            settings=None
        )
        db.add(user_b)
        db.commit()

        # Create session for User A
        token_a = secrets.token_urlsafe(32)
        expires_a = datetime.now(timezone.utc) + timedelta(hours=24)
        session_a = AuthSession(
            user_id=user_a_id,
            session_token=token_a,
            expires_at=expires_a
        )
        db.add(session_a)

        # Create session for User B
        token_b = secrets.token_urlsafe(32)
        expires_b = datetime.now(timezone.utc) + timedelta(hours=24)
        session_b = AuthSession(
            user_id=user_b_id,
            session_token=token_b,
            expires_at=expires_b
        )
        db.add(session_b)
        db.commit()

        return token_a, token_b, user_a_id, user_b_id
    finally:
        db.close()

def cleanup_test_data(user_a_id, user_b_id):
    """Remove test users and their data from DB"""
    db = SessionLocal()
    try:
        # Delete workouts, training blocks, sessions, users
        db.query(Workout).filter(
            Workout.training_block_id.in_(
                db.query(TrainingBlock.id).filter(
                    TrainingBlock.user_id.in_([user_a_id, user_b_id])
                )
            )
        ).delete(synchronize_session=False)

        db.query(TrainingBlock).filter(
            TrainingBlock.user_id.in_([user_a_id, user_b_id])
        ).delete(synchronize_session=False)

        db.query(AuthSession).filter(
            AuthSession.user_id.in_([user_a_id, user_b_id])
        ).delete(synchronize_session=False)

        db.query(User).filter(
            User.id.in_([user_a_id, user_b_id])
        ).delete(synchronize_session=False)

        db.commit()
    finally:
        db.close()

# ============================================================================
# Test Functions
# ============================================================================

def test_data_isolation(token_a, token_b, user_a_id, user_b_id):
    """Test that User B cannot access User A's data"""
    print_header("Data Isolation Tests")

    # Test 1a: Create training block as User A
    block_data = {
        "event_name": "Test Marathon",
        "event_distance": "marathon",
        "target_date": "2026-05-01",
        "start_date": "2026-03-01",
        "total_weeks": 12,
        "phase_map": {
            "base": [1, 2, 3, 4],
            "build": [5, 6, 7, 8],
            "peak": [9, 10, 11],
            "taper": [12]
        }
    }

    headers_a = {"X-Auth-Session": token_a}
    try:
        response = requests.post(
            f"{API_URL}/training-block",
            json=block_data,
            headers=headers_a
        )
        if response.status_code == 201:
            block_id = response.json()['block']['id']
            pass_test("Create training block as User A", f"(block_id: {block_id[:8]}...)")
        else:
            fail_test("Create training block as User A", f"status {response.status_code}")
            return
    except Exception as e:
        fail_test("Create training block as User A", str(e))
        return

    # Test 1b: User B tries to access User A's block via GET /api/training-block
    # (should return null or maintenance mode, not User A's block)
    headers_b = {"X-Auth-Session": token_b}
    try:
        response = requests.get(
            f"{API_URL}/training-block",
            headers=headers_b
        )
        if response.status_code == 200:
            data = response.json()
            block = data.get('block')
            if block is None:
                pass_test("User B gets maintenance mode (no own block)", "returned null")
            elif block['id'] != block_id:
                pass_test("User B isolated from User A's block", "different block_id")
            else:
                fail_test("User B isolated from User A's block", "saw User A's block!")
        else:
            fail_test("User B gets own training block", f"status {response.status_code}")
    except Exception as e:
        fail_test("User B gets own training block", str(e))

    # Test 1c: User B tries direct GET on User A's block overview
    # (should return 404)
    try:
        response = requests.get(
            f"{API_URL}/training-block/{block_id}/overview",
            headers=headers_b
        )
        if response.status_code == 404:
            pass_test("Direct access to User A's block overview by User B", "returned 404")
        else:
            fail_test("Direct access to User A's block overview by User B", f"status {response.status_code}, expected 404")
    except Exception as e:
        fail_test("Direct access to User A's block by User B", str(e))

def test_preferences_crud(token_a):
    """Test preferences read/write/validation"""
    print_header("User Preferences CRUD Tests")

    headers = {"X-Auth-Session": token_a}

    # Test 2a: GET /api/user/profile — should have empty/null preferences initially
    try:
        response = requests.get(
            f"{API_URL}/user/profile",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            prefs = user.get('preferences')
            if prefs is None or prefs == {} or prefs == {'theme': 'light', 'units': 'mi'}:
                pass_test("GET /api/user/profile returns user", f"prefs: {prefs}")
            else:
                pass_test("GET /api/user/profile returns user", f"existing prefs: {prefs}")
        else:
            fail_test("GET /api/user/profile", f"status {response.status_code}")
    except Exception as e:
        fail_test("GET /api/user/profile", str(e))

    # Test 2b: PUT /api/user/preferences with valid data
    valid_prefs = {
        "available_days": ["mon", "wed", "fri", "sat"],
        "experience_level": "intermediate",
        "weekly_mileage_comfort": 40
    }
    try:
        response = requests.put(
            f"{API_URL}/user/preferences",
            json=valid_prefs,
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            returned_prefs = data.get('user', {}).get('preferences', {})
            if (returned_prefs.get('experience_level') == 'intermediate'
                    and returned_prefs.get('weekly_mileage_comfort') == 40
                    and set(returned_prefs.get('available_days', [])) == {"mon", "wed", "fri", "sat"}):
                pass_test("PUT /api/user/preferences (valid data)", "saved successfully")
            else:
                fail_test("PUT /api/user/preferences (valid data)", f"prefs mismatch: {returned_prefs}")
        else:
            fail_test("PUT /api/user/preferences (valid data)", f"status {response.status_code}: {response.text}")
    except Exception as e:
        fail_test("PUT /api/user/preferences (valid data)", str(e))

    # Test 2c: GET /api/user/profile — verify preferences persisted
    try:
        response = requests.get(
            f"{API_URL}/user/profile",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            prefs = data.get('user', {}).get('preferences', {})
            if (prefs.get('experience_level') == 'intermediate'
                    and prefs.get('weekly_mileage_comfort') == 40):
                pass_test("Preferences persisted after PUT", f"level: {prefs.get('experience_level')}, mileage: {prefs.get('weekly_mileage_comfort')}")
            else:
                fail_test("Preferences persisted after PUT", f"got {prefs}")
        else:
            fail_test("GET /api/user/profile (after PUT)", f"status {response.status_code}")
    except Exception as e:
        fail_test("GET /api/user/profile (after PUT)", str(e))

    # Test 2d: PUT /api/user/preferences with invalid data (should be 400)
    invalid_prefs = {
        "experience_level": "grandmaster",
        "available_days": "not_a_list"
    }
    try:
        response = requests.put(
            f"{API_URL}/user/preferences",
            json=invalid_prefs,
            headers=headers
        )
        if response.status_code == 400:
            pass_test("PUT /api/user/preferences (invalid data)", "rejected with 400")
        else:
            fail_test("PUT /api/user/preferences (invalid data)", f"status {response.status_code}, expected 400")
    except Exception as e:
        fail_test("PUT /api/user/preferences (invalid data)", str(e))

def test_session_lifecycle():
    """Test valid/invalid/expired sessions"""
    print_header("Session Lifecycle Tests")

    db = SessionLocal()
    try:
        # Test 3a: Valid session token
        user = User(
            id=uuid.uuid4(),
            email=f"test_session_{uuid.uuid4().hex[:8]}@example.com",
            name="Test Session User",
            google_id=f"google_{uuid.uuid4().hex[:12]}",
            role='beta_tester'
        )
        db.add(user)
        db.commit()

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        session = AuthSession(
            user_id=user.id,
            session_token=token,
            expires_at=expires_at
        )
        db.add(session)
        db.commit()

        headers = {"X-Auth-Session": token}
        try:
            response = requests.get(
                f"{API_URL}/user/profile",
                headers=headers
            )
            if response.status_code == 200:
                pass_test("Valid session token", "authenticated successfully")
            else:
                fail_test("Valid session token", f"status {response.status_code}")
        except Exception as e:
            fail_test("Valid session token", str(e))

        # Test 3b: Invalid session token
        invalid_token = "invalid_token_" + secrets.token_urlsafe(16)
        headers_invalid = {"X-Auth-Session": invalid_token}
        try:
            response = requests.get(
                f"{API_URL}/user/profile",
                headers=headers_invalid
            )
            if response.status_code == 401:
                pass_test("Invalid session token", "returned 401")
            else:
                fail_test("Invalid session token", f"returned {response.status_code}, expected 401")
        except Exception as e:
            fail_test("Invalid session token", str(e))

        # Test 3c: Expired session token
        expired_token = secrets.token_urlsafe(32)
        expired_expires_at = datetime.now(timezone.utc) - timedelta(hours=1)  # 1 hour in past
        expired_session = AuthSession(
            user_id=user.id,
            session_token=expired_token,
            expires_at=expired_expires_at
        )
        db.add(expired_session)
        db.commit()

        headers_expired = {"X-Auth-Session": expired_token}
        try:
            response = requests.get(
                f"{API_URL}/user/profile",
                headers=headers_expired
            )
            if response.status_code == 401:
                pass_test("Expired session token", "returned 401")
            else:
                fail_test("Expired session token", f"returned {response.status_code}, expected 401")
        except Exception as e:
            fail_test("Expired session token", str(e))

        # Test 3d: Missing session token
        try:
            response = requests.get(f"{API_URL}/user/profile")
            if response.status_code == 401:
                pass_test("Missing session token", "returned 401")
            else:
                fail_test("Missing session token", f"returned {response.status_code}, expected 401")
        except Exception as e:
            fail_test("Missing session token", str(e))

        # Cleanup test user
        db.query(AuthSession).filter(AuthSession.user_id == user.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()

    finally:
        db.close()

def test_auth_headers():
    """Test multiple auth header formats"""
    print_header("Authorization Header Format Tests")

    db = SessionLocal()
    try:
        user = User(
            id=uuid.uuid4(),
            email=f"test_headers_{uuid.uuid4().hex[:8]}@example.com",
            name="Test Headers User",
            google_id=f"google_{uuid.uuid4().hex[:12]}",
            role='beta_tester'
        )
        db.add(user)
        db.commit()

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        session = AuthSession(
            user_id=user.id,
            session_token=token,
            expires_at=expires_at
        )
        db.add(session)
        db.commit()

        # Test 4a: Bearer token format
        headers_bearer = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(
                f"{API_URL}/user/profile",
                headers=headers_bearer
            )
            if response.status_code == 200:
                pass_test("Bearer token format", "authenticated")
            else:
                fail_test("Bearer token format", f"status {response.status_code}")
        except Exception as e:
            fail_test("Bearer token format", str(e))

        # Test 4b: X-Auth-Session header format
        headers_x_auth = {"X-Auth-Session": token}
        try:
            response = requests.get(
                f"{API_URL}/user/profile",
                headers=headers_x_auth
            )
            if response.status_code == 200:
                pass_test("X-Auth-Session header format", "authenticated")
            else:
                fail_test("X-Auth-Session header format", f"status {response.status_code}")
        except Exception as e:
            fail_test("X-Auth-Session header format", str(e))

        # Cleanup
        db.query(AuthSession).filter(AuthSession.user_id == user.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()

    finally:
        db.close()

def test_health_check():
    """Verify backend is running"""
    print_header("Health Check")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            pass_test("Backend server is running", "on http://localhost:5000")
            return True
        else:
            fail_test("Backend server health check", f"status {response.status_code}")
            return False
    except Exception as e:
        fail_test("Backend server is running", str(e))
        print("\n  Make sure the backend server is running: python app.py")
        return False

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + " Phase 6 E2E Tests — Multi-User Support & Security ".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")

    # Health check first
    if not test_health_check():
        print_summary()
        sys.exit(1)

    # Setup
    print("\n[SETUP] Creating test users...")
    token_a, token_b, user_a_id, user_b_id = setup_test_users()
    print(f"  Created User A (id: {str(user_a_id)[:8]}...)")
    print(f"  Created User B (id: {str(user_b_id)[:8]}...)")

    try:
        # Run all tests
        test_data_isolation(token_a, token_b, user_a_id, user_b_id)
        test_preferences_crud(token_a)
        test_session_lifecycle()
        test_auth_headers()

    finally:
        # Cleanup
        print("\n[CLEANUP] Removing test data...")
        cleanup_test_data(user_a_id, user_b_id)
        print("  Test users and data removed")

    # Summary
    print_summary()
    sys.exit(0 if failed == 0 else 1)
