from flask import Flask, request, jsonify, send_file, make_response
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
from services.strava_activity_service import StravaActivityService
from database import get_db, init_db
from logging_config import setup_logging, get_logger, log_api_request, log_strava_operation, log_error

load_dotenv()

# Initialize logging
setup_logging()
logger = get_logger('app')

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configure Flask secret key for sessions
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize services
llm_service = LLMService()
excel_service = ExcelService()
strava_service = StravaService()

# Initialize database on startup
with app.app_context():
    try:
        init_db()
        logger.info("Database tables initialized successfully")
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
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Workout Coach API is running"})


# ============================================================================
# Chat / Workout Plan Generation
# ============================================================================

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and generate workout plans"""
    log_api_request('POST', '/api/chat')
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Check plan limit before creating
        db = next(get_db())
        try:
            max_plans = int(os.getenv('MAX_WORKOUT_PLANS', 5))
            limit_check = WorkoutPlanService.check_plan_limit(db, max_plans)

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
                db=db,
                plan_data=workout_plan_data,
                user_id=None  # Single user for MVP
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
            db.close()

    except Exception as e:
        log_error("Error in chat endpoint", e)
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Workout Plans CRUD
# ============================================================================

@app.route('/api/workout-plans', methods=['GET'])
def get_all_workout_plans():
    """Get all workout plans"""
    try:
        db = next(get_db())
        try:
            plans = WorkoutPlanService.get_all_workout_plans(db, user_id=None)
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
            db.close()
    except Exception as e:
        log_error("Error getting workout plans", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workout-plans/active', methods=['GET'])
def get_active_workout_plan():
    """Get the currently active workout plan"""
    try:
        db = next(get_db())
        try:
            plan = WorkoutPlanService.get_active_workout_plan(db, user_id=None)

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
            db.close()
    except Exception as e:
        log_error("Error getting active workout plan", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workout-plans/<plan_id>', methods=['GET'])
def get_workout_plan(plan_id):
    """Retrieve a specific workout plan by ID"""
    try:
        db = next(get_db())
        try:
            plan_uuid = uuid.UUID(plan_id)
            plan = WorkoutPlanService.get_workout_plan(db, plan_uuid)

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
            db.close()
    except Exception as e:
        log_error("Error getting workout plan", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workout-plans/<plan_id>/activate', methods=['POST'])
def activate_workout_plan(plan_id):
    """Set a workout plan as active (deactivates all others)"""
    try:
        db = next(get_db())
        try:
            plan_uuid = uuid.UUID(plan_id)
            plan = WorkoutPlanService.set_active_workout_plan(db, plan_uuid, user_id=None)

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
            db.close()
    except Exception as e:
        log_error("Error activating workout plan", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workout-plans/<plan_id>', methods=['DELETE'])
def delete_workout_plan(plan_id):
    """Delete a workout plan (cannot delete active plan)"""
    try:
        db = next(get_db())
        try:
            plan_uuid = uuid.UUID(plan_id)
            deleted = WorkoutPlanService.delete_workout_plan(db, plan_uuid, user_id=None)

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
            db.close()
    except Exception as e:
        log_error("Error deleting workout plan", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/export/excel/<plan_id>', methods=['GET'])
def export_excel(plan_id):
    """Export workout plan to Excel"""
    try:
        db = next(get_db())
        try:
            plan_uuid = uuid.UUID(plan_id)
            plan = WorkoutPlanService.get_workout_plan(db, plan_uuid)

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
            db.close()

    except Exception as e:
        log_error("Error exporting Excel", e)
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Phase 3: Week View API Endpoints
# ============================================================================

@app.route('/api/workouts/week', methods=['GET'])
def get_workouts_current_week():
    """Get workouts for the current calendar week"""
    try:
        db = next(get_db())
        try:
            week_start, week_end = WorkoutPlanService.get_week_start_end()
            workouts = WorkoutPlanService.get_workouts_for_week(db, week_start, week_end, user_id=None)

            return jsonify({
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'workouts': [w.to_dict() for w in workouts],
                'count': len(workouts)
            })
        finally:
            db.close()
    except Exception as e:
        log_error("Error fetching current week workouts", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workouts/week/<int:week_offset>', methods=['GET'])
def get_workouts_week_offset(week_offset):
    """Get workouts for a specific week by offset (0=current, -1=last, +1=next)"""
    try:
        db = next(get_db())
        try:
            week_start, week_end = WorkoutPlanService.get_week_by_offset(week_offset)
            workouts = WorkoutPlanService.get_workouts_for_week(db, week_start, week_end, user_id=None)

            return jsonify({
                'week_offset': week_offset,
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'workouts': [w.to_dict() for w in workouts],
                'count': len(workouts)
            })
        finally:
            db.close()
    except Exception as e:
        log_error("Error fetching week workouts", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workouts/month/<int:year>/<int:month>', methods=['GET'])
def get_workouts_month(year, month):
    """Get workouts for a specific calendar month"""
    try:
        # Validate month
        if month < 1 or month > 12:
            return jsonify({"error": "Month must be between 1 and 12"}), 400

        db = next(get_db())
        try:
            workouts = WorkoutPlanService.get_workouts_for_month(db, year, month, user_id=None)

            return jsonify({
                'year': year,
                'month': month,
                'workouts': [w.to_dict() for w in workouts],
                'count': len(workouts)
            })
        finally:
            db.close()
    except Exception as e:
        log_error("Error fetching month workouts", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workouts/<workout_id>/complete', methods=['PUT'])
def toggle_workout_completion(workout_id):
    """Toggle workout completion status"""
    try:
        db = next(get_db())
        try:
            workout = WorkoutPlanService.toggle_workout_completion(db, uuid.UUID(workout_id))
            logger.debug(f"Toggled workout completion: {workout_id} -> {workout.is_completed}")
            return jsonify({
                'workout': workout.to_dict(),
                'message': f"Workout marked as {'completed' if workout.is_completed else 'incomplete'}"
            })
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        finally:
            db.close()
    except ValueError as e:
        return jsonify({"error": f"Invalid workout ID: {str(e)}"}), 400
    except Exception as e:
        log_error("Error toggling workout completion", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/workouts/progress', methods=['GET'])
def get_week_progress():
    """Get progress summary for the current week"""
    try:
        db = next(get_db())
        try:
            # Get current week by default, or allow week_offset query param
            week_offset = request.args.get('week_offset', type=int, default=0)
            week_start, week_end = WorkoutPlanService.get_week_by_offset(week_offset)

            progress = WorkoutPlanService.get_week_progress(db, week_start, week_end, user_id=None)

            return jsonify(progress)
        finally:
            db.close()
    except Exception as e:
        log_error("Error fetching week progress", e)
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Phase 4: Workout Editing API
# ============================================================================

@app.route('/api/workouts/<workout_id>', methods=['PUT'])
def update_workout(workout_id):
    """Update workout details (partial updates supported)"""
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Request body is required"}), 400

        # Allow empty body (no fields to update)
        if not data:
            # Just return the workout as-is
            db = next(get_db())
            try:
                workout = WorkoutPlanService.get_workout(db, uuid.UUID(workout_id))
                if not workout:
                    return jsonify({"error": f"Workout with id {workout_id} not found"}), 404
                return jsonify({
                    'workout': workout.to_dict(),
                    'message': 'No fields to update'
                })
            finally:
                db.close()

        db = next(get_db())
        try:
            workout = WorkoutPlanService.update_workout(db, uuid.UUID(workout_id), data)
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
            db.close()
    except ValueError as e:
        return jsonify({"error": f"Invalid workout ID: {str(e)}"}), 400
    except Exception as e:
        log_error("Error updating workout", e)
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Strava Integration Endpoints (Phase 6: Secure Session Management)
# ============================================================================

@app.route('/api/strava/auth', methods=['GET'])
def strava_auth():
    """Initiate Strava OAuth flow"""
    log_strava_operation("auth_init", "Starting OAuth flow")
    auth_url = strava_service.get_authorization_url()
    return jsonify({"auth_url": auth_url})


@app.route('/api/strava/callback', methods=['GET'])
def strava_callback():
    """Handle Strava OAuth callback with server-side token storage"""
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
                        window.location.href = 'http://localhost:3000?strava_connected=true';
                    }}
                </script>
            </body>
        </html>
        """

    except Exception as e:
        log_error("Strava OAuth exception", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/strava/validate', methods=['GET'])
def validate_strava_connection():
    """Validate Strava connection and return athlete info"""
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
def strava_logout():
    """Log out from Strava (delete server-side session)"""
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
def get_strava_activities():
    """Fetch and import activities from Strava"""
    try:
        session_token = get_strava_session_token()
        if not session_token:
            return jsonify({"error": "Session token required"}), 401

        db = next(get_db())
        try:
            session = StravaActivityService.get_session_by_token(db, session_token)
            if not session:
                return jsonify({"error": "Invalid session"}), 401

            if session.is_expired():
                return jsonify({"error": "Session expired"}), 401

            # Fetch activities from Strava API
            log_strava_operation("fetch_activities", "Fetching from Strava API")
            raw_activities = strava_service.get_activities(session.access_token)

            # Import activities to database
            imported = StravaActivityService.import_activities(db, raw_activities, user_id=None)

            log_strava_operation("fetch_activities", f"Imported {len(imported)} activities")

            return jsonify({
                "activities": [a.to_dict() for a in imported],
                "count": len(imported)
            })
        finally:
            db.close()

    except Exception as e:
        log_error("Error fetching Strava activities", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/strava/activities/stored', methods=['GET'])
def get_stored_activities():
    """Get activities stored in the database (no Strava API call)"""
    try:
        limit = request.args.get('limit', type=int, default=100)
        offset = request.args.get('offset', type=int, default=0)

        db = next(get_db())
        try:
            activities = StravaActivityService.get_all_activities(db, user_id=None, limit=limit, offset=offset)
            total_count = StravaActivityService.get_activity_count(db, user_id=None)

            return jsonify({
                "activities": [a.to_dict() for a in activities],
                "count": len(activities),
                "total_count": total_count
            })
        finally:
            db.close()

    except Exception as e:
        log_error("Error getting stored activities", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/strava/activities/<activity_id>/link', methods=['POST'])
def link_activity_to_workout(activity_id):
    """Link a Strava activity to a planned workout"""
    try:
        data = request.json
        workout_id = data.get('workout_id')

        if not workout_id:
            return jsonify({"error": "workout_id is required"}), 400

        db = next(get_db())
        try:
            activity = StravaActivityService.link_activity_to_workout(
                db, uuid.UUID(activity_id), uuid.UUID(workout_id)
            )
            log_strava_operation("link_activity", f"Linked activity {activity_id} to workout {workout_id}")
            return jsonify({
                "activity": activity.to_dict(),
                "message": "Activity linked to workout successfully"
            })
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        finally:
            db.close()

    except ValueError as e:
        return jsonify({"error": f"Invalid ID format: {str(e)}"}), 400
    except Exception as e:
        log_error("Error linking activity to workout", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/strava/activities/<activity_id>/unlink', methods=['POST'])
def unlink_activity(activity_id):
    """Unlink a Strava activity from its workout"""
    try:
        db = next(get_db())
        try:
            activity = StravaActivityService.unlink_activity(db, uuid.UUID(activity_id))
            log_strava_operation("unlink_activity", f"Unlinked activity {activity_id}")
            return jsonify({
                "activity": activity.to_dict(),
                "message": "Activity unlinked successfully"
            })
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        finally:
            db.close()

    except ValueError as e:
        return jsonify({"error": f"Invalid activity ID: {str(e)}"}), 400
    except Exception as e:
        log_error("Error unlinking activity", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/strava/import', methods=['POST'])
def import_strava_activities():
    """Import selected activities (legacy endpoint - now auto-imports on fetch)"""
    try:
        data = request.json
        activity_ids = data.get('activity_ids', [])

        db = next(get_db())
        try:
            imported = []
            for strava_id in activity_ids:
                activity = StravaActivityService.get_activity_by_strava_id(db, str(strava_id))
                if activity:
                    imported.append(activity.to_dict())

            return jsonify({
                "message": f"Found {len(imported)} activities",
                "activities": imported
            })
        finally:
            db.close()

    except Exception as e:
        log_error("Error importing activities", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
