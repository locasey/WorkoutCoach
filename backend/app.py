from flask import Flask, request, jsonify, send_file, make_response, g
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta, timezone
import io
import uuid

from services.llm_service import LLMService
from services.excel_service import ExcelService
from services.strava_service import StravaService
from services.workout_plan_service import WorkoutPlanService
from services.training_block_service import TrainingBlockService
from services.strava_activity_service import StravaActivityService
from services.auth_service import (
    require_auth, require_admin, validate_google_token,
    create_session_for_user, delete_session, get_user_from_session,
    get_session_token_from_request
)
from services.user_service import UserService
from services.invite_code_service import InviteCodeService
from database import get_db, init_db
from logging_config import setup_logging, get_logger, log_api_request, log_strava_operation, log_error

load_dotenv()

# Feature flags (LOC-23)
STRAVA_ENABLED = os.getenv('STRAVA_ENABLED', 'false').lower() == 'true'

# Initialize logging
setup_logging()
logger = get_logger('app')

app = Flask(__name__)

# Configure CORS based on environment
# In production, restrict to specific origins; in development, allow all
cors_origins = os.getenv('CORS_ORIGINS', '*')
if cors_origins and cors_origins != '*':
    # Split comma-separated origins for production
    origins = [origin.strip() for origin in cors_origins.split(',')]
    CORS(app, origins=origins, supports_credentials=True)
else:
    # Development: allow all origins
    CORS(app, supports_credentials=True)

# Configure Flask secret key for sessions
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

@app.teardown_request
def close_db_session(exception=None):
    """Safety net: close DB session if route handler didn't."""
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# Initialize services
llm_service = LLMService()
excel_service = ExcelService()
strava_service = StravaService()

# Initialize database on startup
with app.app_context():
    try:
        init_db()
        logger.info("Database tables initialized successfully")
        # Clean up expired auth sessions on startup
        from services.auth_service import cleanup_expired_sessions
        expired_count = cleanup_expired_sessions()
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired sessions")
    except Exception as e:
        logger.warning(f"Database initialization warning: {str(e)}")
        logger.info("Make sure PostgreSQL is running and DATABASE_URL is set correctly")

# ============================================================================
# Helper: Get session token from request
# ============================================================================

def get_strava_session_token():
    """Extract Strava session token from request headers or cookies"""
    # Try Authorization header first
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]

    # Try X-Strava-Session header
    session_header = request.headers.get('X-Strava-Session')
    if session_header:
        return session_header

    # Try cookie
    return request.cookies.get('strava_session')


# ============================================================================
# Health Check
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint - always accessible, no auth required"""
    return jsonify({"status": "ok", "message": "Workout Coach API is running"})


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.route('/api/auth/google', methods=['POST'])
def auth_google():
    """
    Unified Google OAuth login/signup endpoint.

    Request body:
        {
            "credential": "google_id_token",
            "invite_code": "optional_invite_code",
            "consent": true  // required for new users
        }

    Returns:
        200: { session_token, user } — existing user logged in
        201: { session_token, user } — new user created with invite code
        403: { code: "INVITE_REQUIRED" } — new user, no invite code
        400: Invalid token or invite code
    """
    data = request.json
    if not data or 'credential' not in data:
        return jsonify({"error": "Google credential required"}), 400

    try:
        google_info = validate_google_token(data['credential'])
    except ValueError as e:
        logger.warning(f"Google token validation failed: {e}")
        return jsonify({"error": str(e)}), 400

    db = next(get_db())
    try:
        # Try to find existing user
        user, _ = UserService.get_or_create_by_google(
            db,
            google_id=google_info['google_id'],
            email=google_info['email'],
            name=google_info['name']
        )

        if user:
            # Existing user — create session and return
            session_token = create_session_for_user(db, user.id)
            logger.info(f"User logged in: {user.email}")

            response = jsonify({
                "message": "Login successful",
                "session_token": session_token,
                "user": user.to_dict()
            })
            response.set_cookie(
                'auth_session', session_token,
                httponly=True,
                secure=os.getenv('FLASK_ENV') == 'production',
                samesite='Lax',
                max_age=86400
            )
            return response

        # New user — check for invite code
        invite_code = data.get('invite_code')
        consent = data.get('consent', False)

        if not invite_code:
            return jsonify({
                "code": "INVITE_REQUIRED",
                "message": "An invite code is required to create an account"
            }), 403

        if not consent:
            return jsonify({"error": "You must agree to the terms to create an account"}), 400

        # Create the user first (need user_id for invite code redemption)
        new_user = UserService.create_user(
            db,
            google_id=google_info['google_id'],
            email=google_info['email'],
            name=google_info['name'],
            role='beta_tester',
            invite_code_used=invite_code
        )

        # Validate and use the invite code
        used_invite = InviteCodeService.validate_and_use(db, invite_code, new_user.id)
        if not used_invite:
            db.rollback()
            return jsonify({"error": "Invalid or expired invite code"}), 400

        session_token = create_session_for_user(db, new_user.id)
        logger.info(f"New user created: {new_user.email}")

        response = jsonify({
            "message": "Account created successfully",
            "session_token": session_token,
            "user": new_user.to_dict()
        })
        response.set_cookie(
            'auth_session', session_token,
            httponly=True,
            secure=os.getenv('FLASK_ENV') == 'production',
            samesite='Lax',
            max_age=86400
        )
        return response, 201

    except Exception as e:
        db.rollback()
        log_error("Error in Google auth", e)
        return jsonify({"error": "Authentication failed"}), 500
    finally:
        db.close()


@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """Logout endpoint - invalidates the current session."""
    token = get_session_token_from_request()

    if token:
        delete_session(token)
        logger.info("User logged out")

    response = jsonify({"message": "Logged out successfully"})
    response.delete_cookie('auth_session')
    return response


@app.route('/api/auth/check', methods=['GET'])
def auth_check():
    """Check if current session is valid. Returns user object if authenticated."""
    token = get_session_token_from_request()

    if not token:
        return jsonify({
            "authenticated": False,
            "message": "No session token provided"
        })

    db = next(get_db())
    try:
        user = get_user_from_session(db, token)

        if not user:
            return jsonify({
                "authenticated": False,
                "message": "Session invalid or expired"
            })

        return jsonify({
            "authenticated": True,
            "user": user.to_dict(),
            "message": "Session valid"
        })
    finally:
        db.close()


@app.route('/api/admin/invite-codes', methods=['POST'])
@require_auth
@require_admin
def generate_invite_code():
    """Generate a new invite code (admin only)."""
    try:
        invite = InviteCodeService.generate_code(g.db, created_by=g.current_user_id)
        logger.info(f"Invite code generated by {g.current_user.email}: {invite.code}")
        return jsonify({
            "invite_code": invite.to_dict(),
            "message": "Invite code generated"
        }), 201
    finally:
        g.db.close()


@app.route('/api/admin/invite-codes', methods=['GET'])
@require_auth
@require_admin
def list_invite_codes():
    """List all invite codes (admin only)."""
    try:
        codes = InviteCodeService.get_all_codes(g.db)
        return jsonify({
            "invite_codes": [c.to_dict() for c in codes],
            "count": len(codes)
        })
    finally:
        g.db.close()


# ============================================================================
# User Profile & Preferences
# ============================================================================

@app.route('/api/user/profile', methods=['GET'])
@require_auth
def get_user_profile():
    """Get the current user's profile."""
    try:
        user = UserService.get_by_id(g.db, g.current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"user": user.to_dict()})
    finally:
        g.db.close()


@app.route('/api/user/preferences', methods=['PUT'])
@require_auth
def update_user_preferences():
    """Update the current user's preferences."""
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Request body is required"}), 400

        try:
            user = UserService.update_preferences(g.db, g.current_user_id, data)
            return jsonify({
                "user": user.to_dict(),
                "message": "Preferences updated successfully"
            })
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    finally:
        g.db.close()


# ============================================================================
# Chat / Workout Plan Generation
# ============================================================================

@app.route('/api/chat', methods=['POST'])
@require_auth
def chat():
    """Handle chat messages and generate workout plans"""
    log_api_request('POST', '/api/chat')
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Check plan limit before creating
        try:
            max_plans = int(os.getenv('MAX_WORKOUT_PLANS', 5))
            limit_check = WorkoutPlanService.check_plan_limit(g.db, max_plans, g.current_user_id)

            if limit_check['at_limit']:
                return jsonify({
                    "error": "Maximum workout plans reached",
                    "message": f"You have reached the limit of {max_plans} workout plans. Please delete an existing plan first.",
                    "current_count": limit_check['current_count'],
                    "max_allowed": limit_check['max_allowed'],
                    "existing_plans": limit_check['existing_plans']
                }), 400

            # Generate workout plan using LLM
            workout_plan_data = llm_service.generate_workout_plan(user_message)

            # Save to database
            workout_plan = WorkoutPlanService.create_workout_plan(
                db=g.db,
                plan_data=workout_plan_data,
                user_id=g.current_user_id
            )

            # Convert to dict for response
            plan_dict = workout_plan.to_dict()
            plan_dict['workouts'] = [w.to_dict() for w in workout_plan.workouts]

            logger.info(f"Created workout plan: {workout_plan.id}")
            return jsonify({
                "plan_id": str(workout_plan.id),
                "workout_plan": plan_dict,
                "message": "Workout plan generated and saved successfully"
            })
        finally:
            g.db.close()

    except Exception as e:
        log_error("Error in chat endpoint", e)
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Workout Plans CRUD
# ============================================================================

@app.route('/api/workout-plans', methods=['GET'])
@require_auth
def get_all_workout_plans():
    """Get all workout plans"""
    try:
        try:
            plans = WorkoutPlanService.get_all_workout_plans(g.db, user_id=g.current_user_id)
            max_plans = int(os.getenv('MAX_WORKOUT_PLANS', 5))

            plans_data = []
            for plan in plans:
                plan_dict = plan.to_dict()
                plan_dict['workout_count'] = len(plan.workouts)
                plans_data.append(plan_dict)

            return jsonify({
                "plans": plans_data,
                "count": len(plans_data),
                "max_allowed": max_plans
            })
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error getting workout plans", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workout-plans/active', methods=['GET'])
@require_auth
def get_active_workout_plan():
    """Get the currently active workout plan"""
    try:
        try:
            plan = WorkoutPlanService.get_active_workout_plan(g.db, user_id=g.current_user_id)

            if not plan:
                return jsonify({
                    "message": "No active workout plan",
                    "plan": None
                }), 200

            plan_dict = plan.to_dict()
            plan_dict['workouts'] = [w.to_dict() for w in plan.workouts]

            return jsonify({
                "plan": plan_dict,
                "message": "Active workout plan retrieved successfully"
            })
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error getting active workout plan", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workout-plans/<plan_id>', methods=['GET'])
@require_auth
def get_workout_plan(plan_id):
    """Retrieve a specific workout plan by ID"""
    try:
        try:
            plan_uuid = uuid.UUID(plan_id)
            plan = WorkoutPlanService.get_workout_plan(g.db, plan_uuid, user_id=g.current_user_id)

            if not plan:
                return jsonify({"error": "Workout plan not found"}), 404

            plan_dict = plan.to_dict()
            plan_dict['workouts'] = [w.to_dict() for w in plan.workouts]

            return jsonify({
                "plan": plan_dict,
                "message": "Workout plan retrieved successfully"
            })
        except ValueError as e:
            return jsonify({"error": f"Invalid plan ID: {str(e)}"}), 400
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error getting workout plan", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workout-plans/<plan_id>/activate', methods=['POST'])
@require_auth
def activate_workout_plan(plan_id):
    """Set a workout plan as active (deactivates all others)"""
    try:
        try:
            plan_uuid = uuid.UUID(plan_id)
            plan = WorkoutPlanService.set_active_workout_plan(g.db, plan_uuid, user_id=g.current_user_id)

            plan_dict = plan.to_dict()
            plan_dict['workouts'] = [w.to_dict() for w in plan.workouts]

            logger.info(f"Activated workout plan: {plan_id}")
            return jsonify({
                "plan": plan_dict,
                "message": "Workout plan activated successfully"
            })
        except ValueError as e:
            if "not found" in str(e).lower():
                return jsonify({"error": str(e)}), 404
            return jsonify({"error": f"Invalid plan ID: {str(e)}"}), 400
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error activating workout plan", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workout-plans/<plan_id>', methods=['PATCH'])
@require_auth
def update_workout_plan(plan_id):
    """
    Update workout plan details (currently supports name only).

    Request body:
        {
            "name": "New Plan Name"
        }

    Returns:
        Updated plan object
    """
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Request body is required"}), 400

        try:
            plan_uuid = uuid.UUID(plan_id)

            # Currently only name is editable
            if 'name' in data:
                plan = WorkoutPlanService.update_workout_plan_name(
                    g.db, plan_uuid, data['name'], user_id=g.current_user_id
                )
            else:
                # If no fields to update, just return the current plan
                plan = WorkoutPlanService.get_workout_plan(g.db, plan_uuid, user_id=g.current_user_id)
                if not plan:
                    return jsonify({"error": "Workout plan not found"}), 404

            plan_dict = plan.to_dict()
            plan_dict['workout_count'] = len(plan.workouts)

            logger.info(f"Updated workout plan: {plan_id}")
            return jsonify({
                "plan": plan_dict,
                "message": "Workout plan updated successfully"
            })
        except ValueError as e:
            error_msg = str(e)
            if "not found" in error_msg.lower():
                return jsonify({"error": error_msg}), 404
            return jsonify({"error": error_msg}), 400
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error updating workout plan", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workout-plans/<plan_id>', methods=['DELETE'])
@require_auth
def delete_workout_plan(plan_id):
    """Delete a workout plan (cannot delete active plan)"""
    try:
        try:
            plan_uuid = uuid.UUID(plan_id)
            deleted = WorkoutPlanService.delete_workout_plan(g.db, plan_uuid, user_id=g.current_user_id)

            if not deleted:
                return jsonify({"error": "Workout plan not found"}), 404

            logger.info(f"Deleted workout plan: {plan_id}")
            return jsonify({
                "message": "Workout plan deleted successfully",
                "deleted_plan_id": plan_id
            })
        except ValueError as e:
            if "active" in str(e).lower():
                return jsonify({"error": str(e)}), 400
            return jsonify({"error": f"Invalid plan ID: {str(e)}"}), 400
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error deleting workout plan", e)
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Training Block API Endpoints (New Architecture)
# ============================================================================

@app.route('/api/training-block', methods=['GET'])
@require_auth
def get_training_block():
    """Get the current active training block (or null if in maintenance mode)"""
    try:
        try:
            block = TrainingBlockService.get_active_block(g.db, user_id=g.current_user_id)

            if not block:
                return jsonify({
                    "block": None,
                    "mode": "maintenance",
                    "message": "No active training block - in maintenance mode"
                }), 200

            return jsonify({
                "block": block.to_dict(),
                "mode": "training",
                "message": "Active training block retrieved"
            })
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error getting training block", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/training-block', methods=['POST'])
@require_auth
def create_training_block():
    """Create a new training block (starts training mode)"""
    try:
        data = request.get_json()

        required_fields = ['event_name', 'event_distance', 'target_date', 'total_weeks', 'phase_map']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        try:
            from datetime import datetime
            target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
            start_date = None
            if data.get('start_date'):
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()

            block = TrainingBlockService.create_training_block(
                db=g.db,
                event_name=data['event_name'],
                event_distance=data['event_distance'],
                target_date=target_date,
                total_weeks=data['total_weeks'],
                phase_map=data['phase_map'],
                start_date=start_date,
                user_id=g.current_user_id
            )

            logger.info(f"Created training block: {block.id} for {data['event_name']}")
            return jsonify({
                "block": block.to_dict(),
                "message": "Training block created successfully"
            }), 201
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error creating training block", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/training-block/<block_id>', methods=['PUT'])
@require_auth
def update_training_block(block_id):
    """Update a training block"""
    try:
        data = request.get_json()
        try:
            block_uuid = uuid.UUID(block_id)
            # Verify ownership before updating
            existing = TrainingBlockService.get_block_by_id(g.db, block_uuid, user_id=g.current_user_id)
            if not existing:
                return jsonify({"error": "Training block not found"}), 404
            block = TrainingBlockService.update_training_block(g.db, block_uuid, **data)

            logger.info(f"Updated training block: {block_id}")
            return jsonify({
                "block": block.to_dict(),
                "message": "Training block updated successfully"
            })
        except ValueError as e:
            return jsonify({"error": f"Invalid block ID: {str(e)}"}), 400
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error updating training block", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/training-block/<block_id>/phases', methods=['PUT'])
@require_auth
def update_training_block_phases(block_id):
    """Update the phase structure of a training block"""
    try:
        data = request.get_json()

        if 'phase_map' not in data:
            return jsonify({"error": "Missing required field: phase_map"}), 400

        try:
            block_uuid = uuid.UUID(block_id)
            # Verify ownership before updating phases
            existing = TrainingBlockService.get_block_by_id(g.db, block_uuid, user_id=g.current_user_id)
            if not existing:
                return jsonify({"error": "Training block not found"}), 404
            block = TrainingBlockService.update_phases(g.db, block_uuid, data['phase_map'])

            logger.info(f"Updated phases for training block: {block_id}")
            return jsonify({
                "block": block.to_dict(),
                "message": "Training block phases updated successfully"
            })
        except ValueError as e:
            return jsonify({"error": f"Invalid block ID: {str(e)}"}), 400
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error updating training block phases", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/training-block/<block_id>', methods=['DELETE'])
@require_auth
def delete_training_block(block_id):
    """End a training block (abandon it)"""
    try:
        data = request.get_json() or {}
        completed = data.get('completed', False)

        try:
            block_uuid = uuid.UUID(block_id)
            # Verify ownership before ending
            existing = TrainingBlockService.get_block_by_id(g.db, block_uuid, user_id=g.current_user_id)
            if not existing:
                return jsonify({"error": "Training block not found"}), 404
            block = TrainingBlockService.end_training_block(g.db, block_uuid, completed=completed)

            status = "completed" if completed else "abandoned"
            logger.info(f"Ended training block: {block_id} (status: {status})")
            return jsonify({
                "block": block.to_dict(),
                "message": f"Training block {status}"
            })
        except ValueError as e:
            return jsonify({"error": f"Invalid block ID: {str(e)}"}), 400
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error ending training block", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/training-block/<block_id>/overview', methods=['GET'])
@require_auth
def get_training_block_overview(block_id):
    """Get full training block overview for visualization"""
    try:
        try:
            block_uuid = uuid.UUID(block_id)
            # Verify ownership before returning overview
            existing = TrainingBlockService.get_block_by_id(g.db, block_uuid, user_id=g.current_user_id)
            if not existing:
                return jsonify({"error": "Training block not found"}), 404
            overview = TrainingBlockService.get_block_overview(g.db, block_uuid)

            return jsonify(overview)
        except ValueError as e:
            return jsonify({"error": f"Invalid block ID: {str(e)}"}), 400
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error getting training block overview", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/week', methods=['GET'])
@require_auth
def get_week_view():
    """
    Get unified weekly view (works for both training and maintenance modes).

    Query params:
        offset: Week offset from current (0=current, -1=last week, +1=next week)
    """
    try:
        offset = request.args.get('offset', 0, type=int)

        try:
            context = TrainingBlockService.get_week_context(g.db, week_offset=offset, user_id=g.current_user_id)
            return jsonify(context)
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error getting week view", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/training-block/<block_id>/generate-workouts', methods=['POST'])
@require_auth
def generate_block_workouts(block_id):
    """Generate periodized workouts for a training block using LLM."""
    try:
        data = request.json or {}
        experience_level = data.get('experience_level', 'intermediate')

        try:
            from services.periodized_workout_service import PeriodizedWorkoutService
            block_uuid = uuid.UUID(block_id)
            result = PeriodizedWorkoutService.generate_workouts_for_block(
                db=g.db,
                block_id=block_uuid,
                experience_level=experience_level,
                llm_service=llm_service,
                user_id=g.current_user_id
            )
            logger.info(f"Generated {result['workouts_created']} workouts for block {block_id}")
            return jsonify(result)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        finally:
            g.db.close()
    except ValueError as e:
        return jsonify({"error": f"Invalid block ID: {str(e)}"}), 400
    except Exception as e:
        log_error("Error generating block workouts", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/week/regenerate', methods=['POST'])
@require_auth
def regenerate_week():
    """Regenerate workouts for a specific week (snapshots old, LLM generates new)."""
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Request body is required"}), 400

        week_offset = data.get('week_offset', 0)
        reason = data.get('reason', '')

        try:
            # Get active block
            block = TrainingBlockService.get_active_block(g.db, user_id=g.current_user_id)
            if not block:
                return jsonify({"error": "No active training block"}), 400

            result = TrainingBlockService.regenerate_week(
                db=g.db,
                block_id=block.id,
                week_offset=week_offset,
                reason=reason,
                llm_service=llm_service,
                user_id=g.current_user_id
            )
            logger.info(f"Regenerated week (offset={week_offset}) for block {block.id}")
            return jsonify(result)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error regenerating week", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/export/excel/<plan_id>', methods=['GET'])
@require_auth
def export_excel(plan_id):
    """Export workout plan to Excel"""
    try:
        try:
            plan_uuid = uuid.UUID(plan_id)
            plan = WorkoutPlanService.get_workout_plan(g.db, plan_uuid, user_id=g.current_user_id)

            if not plan:
                return jsonify({"error": "Workout plan not found"}), 404

            # Convert to dict format expected by Excel service
            plan_dict = plan.to_dict()
            plan_dict['workouts'] = [w.to_dict() for w in plan.workouts]

            excel_file = excel_service.create_workout_plan_excel(plan_dict)

            logger.info(f"Exported workout plan to Excel: {plan_id}")
            return send_file(
                excel_file,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'workout_plan_{plan_id}.xlsx'
            )
        except ValueError as e:
            return jsonify({"error": f"Invalid plan ID: {str(e)}"}), 400
        finally:
            g.db.close()

    except Exception as e:
        log_error("Error exporting Excel", e)
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Phase 3: Week View API Endpoints
# ============================================================================

@app.route('/api/workouts/week', methods=['GET'])
@require_auth
def get_workouts_current_week():
    """Get workouts for the current calendar week"""
    try:
        try:
            week_start, week_end = WorkoutPlanService.get_week_start_end()
            workouts = WorkoutPlanService.get_workouts_for_week(g.db, week_start, week_end, user_id=g.current_user_id)

            return jsonify({
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'workouts': [w.to_dict() for w in workouts],
                'count': len(workouts)
            })
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error fetching current week workouts", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workouts/week/<int:week_offset>', methods=['GET'])
@require_auth
def get_workouts_week_offset(week_offset):
    """Get workouts for a specific week by offset (0=current, -1=last, +1=next)"""
    try:
        try:
            week_start, week_end = WorkoutPlanService.get_week_by_offset(week_offset)
            workouts = WorkoutPlanService.get_workouts_for_week(g.db, week_start, week_end, user_id=g.current_user_id)

            return jsonify({
                'week_offset': week_offset,
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'workouts': [w.to_dict() for w in workouts],
                'count': len(workouts)
            })
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error fetching week workouts", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workouts/month/<int:year>/<int:month>', methods=['GET'])
@require_auth
def get_workouts_month(year, month):
    """Get workouts for a specific calendar month"""
    try:
        # Validate month
        if month < 1 or month > 12:
            return jsonify({"error": "Month must be between 1 and 12"}), 400

        try:
            workouts = WorkoutPlanService.get_workouts_for_month(g.db, year, month, user_id=g.current_user_id)

            return jsonify({
                'year': year,
                'month': month,
                'workouts': [w.to_dict() for w in workouts],
                'count': len(workouts)
            })
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error fetching month workouts", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workouts/<workout_id>/complete', methods=['PUT'])
@require_auth
def toggle_workout_completion(workout_id):
    """Toggle workout completion status"""
    try:
        try:
            workout = WorkoutPlanService.toggle_workout_completion(g.db, uuid.UUID(workout_id), user_id=g.current_user_id)
            logger.debug(f"Toggled workout completion: {workout_id} -> {workout.is_completed}")
            return jsonify({
                'workout': workout.to_dict(),
                'message': f"Workout marked as {'completed' if workout.is_completed else 'incomplete'}"
            })
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        finally:
            g.db.close()
    except ValueError as e:
        return jsonify({"error": f"Invalid workout ID: {str(e)}"}), 400
    except Exception as e:
        log_error("Error toggling workout completion", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workouts/progress', methods=['GET'])
@require_auth
def get_week_progress():
    """Get progress summary for the current week"""
    try:
        try:
            # Get current week by default, or allow week_offset query param
            week_offset = request.args.get('week_offset', type=int, default=0)
            week_start, week_end = WorkoutPlanService.get_week_by_offset(week_offset)

            progress = WorkoutPlanService.get_week_progress(g.db, week_start, week_end, user_id=g.current_user_id)

            return jsonify(progress)
        finally:
            g.db.close()
    except Exception as e:
        log_error("Error fetching week progress", e)
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Phase 4: Workout Editing API
# ============================================================================

@app.route('/api/workouts/<workout_id>', methods=['PUT'])
@require_auth
def update_workout(workout_id):
    """Update workout details (partial updates supported)"""
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Request body is required"}), 400

        # Allow empty body (no fields to update)
        if not data:
            # Just return the workout as-is
            try:
                workout = WorkoutPlanService.get_workout(g.db, uuid.UUID(workout_id), user_id=g.current_user_id)
                if not workout:
                    return jsonify({"error": f"Workout with id {workout_id} not found"}), 404
                return jsonify({
                    'workout': workout.to_dict(),
                    'message': 'No fields to update'
                })
            finally:
                g.db.close()

        try:
            workout = WorkoutPlanService.update_workout(g.db, uuid.UUID(workout_id), data, user_id=g.current_user_id)
            logger.debug(f"Updated workout: {workout_id}")
            return jsonify({
                'workout': workout.to_dict(),
                'message': 'Workout updated successfully'
            })
        except ValueError as e:
            error_msg = str(e)
            if "not found" in error_msg:
                return jsonify({"error": error_msg}), 404
            else:
                # Validation errors
                return jsonify({"error": error_msg}), 400
        finally:
            g.db.close()
    except ValueError as e:
        return jsonify({"error": f"Invalid workout ID: {str(e)}"}), 400
    except Exception as e:
        log_error("Error updating workout", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workouts/day', methods=['POST'])
@require_auth
def add_workout_to_day():
    """
    Add an additional workout to a specific day.

    Supports both training block and legacy workout plan modes.
    Supports up to 2 workouts per day. When adding a second workout:
    - Existing workout gets slot=1 (AM)
    - New workout gets slot=2 (PM)

    Request body:
        {
            "training_block_id": "uuid",   # New architecture (preferred)
            "workout_plan_id": "uuid",     # Legacy fallback
            "scheduled_date": "YYYY-MM-DD",
            "type": "string",
            "duration_minutes": int,
            "distance_km": float,
            "pace": "string",
            "notes": "string"
        }
    """
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Request body is required"}), 400

        if 'scheduled_date' not in data or not data['scheduled_date']:
            return jsonify({"error": "Missing required field: scheduled_date"}), 400

        training_block_id = data.get('training_block_id')
        workout_plan_id = data.get('workout_plan_id')

        if not training_block_id and not workout_plan_id:
            return jsonify({"error": "Either training_block_id or workout_plan_id is required"}), 400

        try:
            if training_block_id:
                # New architecture: add workout to training block
                from models.workout import Workout
                block_uuid = uuid.UUID(training_block_id)
                block = TrainingBlockService.get_block_by_id(g.db, block_uuid, user_id=g.current_user_id)
                if not block:
                    return jsonify({"error": "Training block not found"}), 404
                if block.status != 'active':
                    return jsonify({"error": "Training block is not active"}), 400

                from datetime import datetime as dt
                scheduled_date = dt.fromisoformat(data['scheduled_date']).date()

                # Check existing workouts for this day (max 2)
                existing = g.db.query(Workout).filter(
                    Workout.training_block_id == block_uuid,
                    Workout.scheduled_date == scheduled_date
                ).order_by(Workout.slot.asc().nullslast()).all()

                if len(existing) >= 2:
                    return jsonify({"error": "Maximum 2 workouts per day"}), 400

                # Assign slot
                slot = None
                if len(existing) == 1:
                    # Promote existing to slot 1, new gets slot 2
                    if existing[0].slot is None:
                        existing[0].slot = 1
                    slot = 2

                # Calculate week number from block start
                days_from_start = (scheduled_date - block.start_date).days
                week_number = (days_from_start // 7) + 1
                day_of_week = scheduled_date.weekday() + 1  # 1=Monday

                # Determine phase
                phase = None
                if block.phase_map:
                    for phase_name, weeks in block.phase_map.items():
                        if week_number in weeks:
                            phase = phase_name
                            break

                workout = Workout(
                    training_block_id=block_uuid,
                    week=week_number,
                    day=day_of_week,
                    slot=slot,
                    phase=phase,
                    type=data.get('type', 'easy_run'),
                    distance_km=data.get('distance_km'),
                    duration_minutes=data.get('duration_minutes'),
                    pace=data.get('pace'),
                    notes=data.get('notes'),
                    scheduled_date=scheduled_date,
                    user_id=g.current_user_id
                )
                g.db.add(workout)
                g.db.commit()
                g.db.refresh(workout)
            else:
                # Legacy path: workout plan
                workout = WorkoutPlanService.add_workout_to_day(
                    db=g.db,
                    workout_plan_id=uuid.UUID(workout_plan_id),
                    scheduled_date=data['scheduled_date'],
                    workout_data=data,
                    user_id=g.current_user_id
                )

            logger.info(f"Added workout to day: {data['scheduled_date']} (slot={workout.slot})")
            return jsonify({
                'workout': workout.to_dict(),
                'message': 'Workout added successfully'
            }), 201
        except ValueError as e:
            error_msg = str(e)
            if "not found" in error_msg.lower():
                return jsonify({"error": error_msg}), 404
            return jsonify({"error": error_msg}), 400
        finally:
            g.db.close()

    except ValueError as e:
        return jsonify({"error": f"Invalid ID format: {str(e)}"}), 400
    except Exception as e:
        log_error("Error adding workout to day", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workouts/<workout_id>', methods=['DELETE'])
@require_auth
def delete_workout(workout_id):
    """
    Delete a workout (LOC-22: Supports multiple workouts per day).

    When deleting one of two workouts on a day, the remaining workout's
    slot is demoted back to NULL (single workout display).

    Returns:
        Success message with deleted workout ID
    """
    try:
        try:
            WorkoutPlanService.delete_workout(g.db, uuid.UUID(workout_id), user_id=g.current_user_id)

            logger.info(f"Deleted workout: {workout_id}")
            return jsonify({
                'message': 'Workout deleted successfully',
                'deleted_workout_id': workout_id
            })
        except ValueError as e:
            error_msg = str(e)
            if "not found" in error_msg.lower():
                return jsonify({"error": error_msg}), 404
            return jsonify({"error": error_msg}), 400
        finally:
            g.db.close()

    except ValueError as e:
        return jsonify({"error": f"Invalid workout ID: {str(e)}"}), 400
    except Exception as e:
        log_error("Error deleting workout", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workouts/day/<scheduled_date>', methods=['GET'])
@require_auth
def get_workouts_for_day(scheduled_date):
    """
    Get all workouts for a specific day (LOC-22).

    Args:
        scheduled_date: ISO date string (YYYY-MM-DD)

    Returns:
        List of workouts for the day, ordered by slot
    """
    try:
        try:
            # Get active plan
            active_plan = WorkoutPlanService.get_active_workout_plan(g.db, user_id=g.current_user_id)
            if not active_plan:
                return jsonify({
                    'workouts': [],
                    'count': 0,
                    'message': 'No active workout plan'
                })

            # Parse date
            from datetime import datetime as dt
            try:
                target_date = dt.fromisoformat(scheduled_date).date()
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

            workouts = WorkoutPlanService.get_workouts_for_day(
                g.db, active_plan.id, target_date
            )

            return jsonify({
                'scheduled_date': scheduled_date,
                'workouts': [w.to_dict() for w in workouts],
                'count': len(workouts)
            })
        finally:
            g.db.close()

    except Exception as e:
        log_error("Error getting workouts for day", e)
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Strava Integration Endpoints (Phase 6: Secure Session Management)
# ============================================================================


def check_strava_enabled():
    """
    Guard function to return 404 if Strava feature is disabled.

    Returns 404 (not 403) to avoid revealing that Strava routes exist
    when the feature is disabled - prevents reconnaissance vectors.
    See LOC-23 documentation for rationale.
    """
    if not STRAVA_ENABLED:
        from flask import abort
        abort(404)

@app.route('/api/strava/auth', methods=['GET'])
@require_auth
def strava_auth():
    """Initiate Strava OAuth flow"""
    check_strava_enabled()
    log_strava_operation("auth_init", "Starting OAuth flow")
    auth_url = strava_service.get_authorization_url()
    return jsonify({"auth_url": auth_url})


@app.route('/api/strava/callback', methods=['GET'])
def strava_callback():
    """Handle Strava OAuth callback with server-side token storage"""
    check_strava_enabled()
    try:
        code = request.args.get('code')
        error = request.args.get('error')

        if error:
            log_strava_operation("oauth_callback", f"Error: {error}", success=False)
            return jsonify({"error": f"Strava authorization error: {error}"}), 400

        if not code:
            log_strava_operation("oauth_callback", "No authorization code", success=False)
            return jsonify({"error": "Authorization code not provided"}), 400

        log_strava_operation("oauth_callback", "Exchanging code for token")

        # Exchange code for access token
        token_data = strava_service.exchange_code_for_token(code)
        access_token = token_data.get('access_token') if isinstance(token_data, dict) else token_data

        if not access_token:
            log_strava_operation("oauth_callback", "Failed to get access token", success=False)
            return jsonify({"error": "Failed to obtain access token"}), 500

        # Get athlete info
        athlete_info = {}
        try:
            athlete_info = strava_service.get_athlete_info(access_token)
            log_strava_operation("oauth_callback", f"Connected as {athlete_info.get('firstname', '')} {athlete_info.get('lastname', '')}")
        except Exception as validation_error:
            logger.warning(f"Strava token validation warning: {str(validation_error)}")

        # Calculate token expiration
        expires_at = None
        if isinstance(token_data, dict) and 'expires_at' in token_data:
            expires_at = datetime.fromtimestamp(token_data['expires_at'], tz=timezone.utc)
        elif isinstance(token_data, dict) and 'expires_in' in token_data:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_data['expires_in'])

        # Store session in database (server-side token storage)
        db = next(get_db())
        try:
            # Delete any existing sessions for this user (MVP: single user)
            existing_session = StravaActivityService.get_session_for_user(db, user_id=None)
            if existing_session:
                StravaActivityService.delete_session(db, existing_session.session_token)

            # Create new session
            session = StravaActivityService.create_session(
                db=db,
                access_token=access_token,
                refresh_token=token_data.get('refresh_token') if isinstance(token_data, dict) else None,
                expires_at=expires_at,
                athlete_id=str(athlete_info.get('id', '')),
                athlete_firstname=athlete_info.get('firstname', ''),
                athlete_lastname=athlete_info.get('lastname', ''),
                user_id=None
            )

            session_token = session.session_token
            log_strava_operation("session_create", f"Created session for athlete {athlete_info.get('id', 'unknown')}")
        finally:
            db.close()

        # Get frontend URL from environment (default to localhost for development)
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')

        # Return HTML that stores the session token securely
        return f"""
        <html>
            <body>
                <h2>Successfully authenticated with Strava!</h2>
                <p>You can close this window and return to the app.</p>
                <script>
                    // Pass session token to parent window
                    if (window.opener) {{
                        window.opener.postMessage({{
                            type: 'strava_session',
                            sessionToken: '{session_token}',
                            athlete: {{
                                id: '{athlete_info.get("id", "")}',
                                firstname: '{athlete_info.get("firstname", "")}',
                                lastname: '{athlete_info.get("lastname", "")}'
                            }}
                        }}, '*');
                        window.close();
                    }} else {{
                        // Store session token (not the actual access token)
                        localStorage.setItem('strava_session_token', '{session_token}');
                        window.location.href = '{frontend_url}?strava_connected=true';
                    }}
                </script>
            </body>
        </html>
        """

    except Exception as e:
        log_error("Strava OAuth exception", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/strava/validate', methods=['GET'])
@require_auth
def validate_strava_connection():
    """Validate Strava connection and return athlete info"""
    check_strava_enabled()
    try:
        session_token = get_strava_session_token()
        if not session_token:
            return jsonify({"error": "Session token required", "valid": False}), 401

        db = next(get_db())
        try:
            session = StravaActivityService.get_session_by_token(db, session_token)
            if not session:
                return jsonify({"error": "Invalid session", "valid": False}), 401

            # Check if session is expired
            if session.is_expired():
                # TODO: Implement token refresh using refresh_token
                log_strava_operation("validate", "Session expired", success=False)
                return jsonify({"error": "Session expired", "valid": False}), 401

            log_strava_operation("validate", f"Valid session for athlete {session.athlete_id}")
            return jsonify({
                "valid": True,
                "athlete": {
                    "id": session.athlete_id,
                    "firstname": session.athlete_firstname,
                    "lastname": session.athlete_lastname
                },
                "message": "Strava connection is valid"
            })
        finally:
            db.close()

    except Exception as e:
        log_error("Strava validation error", e)
        return jsonify({
            "valid": False,
            "error": str(e),
            "message": "Strava connection validation failed"
        }), 401


@app.route('/api/strava/logout', methods=['POST'])
@require_auth
def strava_logout():
    """Log out from Strava (delete server-side session)"""
    check_strava_enabled()
    try:
        session_token = get_strava_session_token()
        if not session_token:
            return jsonify({"message": "No active session"}), 200

        db = next(get_db())
        try:
            deleted = StravaActivityService.delete_session(db, session_token)
            if deleted:
                log_strava_operation("logout", "Session deleted successfully")
            return jsonify({"message": "Logged out successfully"})
        finally:
            db.close()

    except Exception as e:
        log_error("Strava logout error", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/strava/activities', methods=['GET'])
@require_auth
def get_strava_activities():
    """Fetch and import activities from Strava"""
    check_strava_enabled()
    try:
        session_token = get_strava_session_token()
        if not session_token:
            return jsonify({"error": "Session token required"}), 401

        try:
            session = StravaActivityService.get_session_by_token(g.db, session_token)
            if not session:
                return jsonify({"error": "Invalid session"}), 401

            if session.is_expired():
                return jsonify({"error": "Session expired"}), 401

            # Fetch activities from Strava API
            log_strava_operation("fetch_activities", "Fetching from Strava API")
            raw_activities = strava_service.get_activities(session.access_token)

            # Import activities to database
            imported = StravaActivityService.import_activities(g.db, raw_activities, user_id=g.current_user_id)

            log_strava_operation("fetch_activities", f"Imported {len(imported)} activities")

            return jsonify({
                "activities": [a.to_dict() for a in imported],
                "count": len(imported)
            })
        finally:
            g.db.close()

    except Exception as e:
        log_error("Error fetching Strava activities", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/strava/activities/stored', methods=['GET'])
@require_auth
def get_stored_activities():
    """Get activities stored in the database (no Strava API call)"""
    check_strava_enabled()
    try:
        limit = request.args.get('limit', type=int, default=100)
        offset = request.args.get('offset', type=int, default=0)

        try:
            activities = StravaActivityService.get_all_activities(g.db, user_id=g.current_user_id, limit=limit, offset=offset)
            total_count = StravaActivityService.get_activity_count(g.db, user_id=g.current_user_id)

            return jsonify({
                "activities": [a.to_dict() for a in activities],
                "count": len(activities),
                "total_count": total_count
            })
        finally:
            g.db.close()

    except Exception as e:
        log_error("Error getting stored activities", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/strava/activities/<activity_id>/link', methods=['POST'])
@require_auth
def link_activity_to_workout(activity_id):
    """Link a Strava activity to a planned workout"""
    check_strava_enabled()
    try:
        data = request.json
        workout_id = data.get('workout_id')

        if not workout_id:
            return jsonify({"error": "workout_id is required"}), 400

        try:
            activity = StravaActivityService.link_activity_to_workout(
                g.db, uuid.UUID(activity_id), uuid.UUID(workout_id)
            )
            log_strava_operation("link_activity", f"Linked activity {activity_id} to workout {workout_id}")
            return jsonify({
                "activity": activity.to_dict(),
                "message": "Activity linked to workout successfully"
            })
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        finally:
            g.db.close()

    except ValueError as e:
        return jsonify({"error": f"Invalid ID format: {str(e)}"}), 400
    except Exception as e:
        log_error("Error linking activity to workout", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/strava/activities/<activity_id>/unlink', methods=['POST'])
@require_auth
def unlink_activity(activity_id):
    """Unlink a Strava activity from its workout"""
    check_strava_enabled()
    try:
        try:
            activity = StravaActivityService.unlink_activity(g.db, uuid.UUID(activity_id))
            log_strava_operation("unlink_activity", f"Unlinked activity {activity_id}")
            return jsonify({
                "activity": activity.to_dict(),
                "message": "Activity unlinked successfully"
            })
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        finally:
            g.db.close()

    except ValueError as e:
        return jsonify({"error": f"Invalid activity ID: {str(e)}"}), 400
    except Exception as e:
        log_error("Error unlinking activity", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/strava/import', methods=['POST'])
@require_auth
def import_strava_activities():
    """Import selected activities (legacy endpoint - now auto-imports on fetch)"""
    check_strava_enabled()
    try:
        data = request.json
        activity_ids = data.get('activity_ids', [])

        try:
            imported = []
            for strava_id in activity_ids:
                activity = StravaActivityService.get_activity_by_strava_id(g.db, str(strava_id))
                if activity:
                    imported.append(activity.to_dict())

            return jsonify({
                "message": f"Found {len(imported)} activities",
                "activities": imported
            })
        finally:
            g.db.close()

    except Exception as e:
        log_error("Error importing activities", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
