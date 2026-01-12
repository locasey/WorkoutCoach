from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import io
import uuid

from services.llm_service import LLMService
from services.excel_service import ExcelService
from services.strava_service import StravaService
from services.workout_plan_service import WorkoutPlanService
from database import get_db, init_db

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize services
llm_service = LLMService()
excel_service = ExcelService()
strava_service = StravaService()

# Legacy in-memory storage (kept for Strava activities only - will be migrated to DB later)
imported_activities = []

# Initialize database on startup
with app.app_context():
    try:
        init_db()
        print("✅ Database tables initialized")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {str(e)}")
        print("   Make sure PostgreSQL is running and DATABASE_URL is set correctly")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Workout Coach API is running"})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and generate workout plans"""
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
            
            return jsonify({
                "plan_id": str(workout_plan.id),
                "workout_plan": plan_dict,
                "message": "Workout plan generated and saved successfully"
            })
        finally:
            db.close()
    
    except Exception as e:
        print(f"❌ Error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

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
        print(f"❌ Error getting workout plans: {str(e)}")
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
        print(f"❌ Error getting active workout plan: {str(e)}")
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
        print(f"❌ Error getting workout plan: {str(e)}")
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
        print(f"❌ Error activating workout plan: {str(e)}")
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
        print(f"❌ Error deleting workout plan: {str(e)}")
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
        print(f"❌ Error exporting Excel: {str(e)}")
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
        print(f"❌ Error fetching current week workouts: {str(e)}")
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
        print(f"❌ Error fetching week workouts: {str(e)}")
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
        print(f"❌ Error fetching month workouts: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/workouts/<workout_id>/complete', methods=['PUT'])
def toggle_workout_completion(workout_id):
    """Toggle workout completion status"""
    try:
        db = next(get_db())
        try:
            workout = WorkoutPlanService.toggle_workout_completion(db, uuid.UUID(workout_id))
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
        print(f"❌ Error toggling workout completion: {str(e)}")
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
        print(f"❌ Error fetching week progress: {str(e)}")
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
        print(f"❌ Error updating workout: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# Strava Integration Endpoints
# ============================================================================

@app.route('/api/strava/auth', methods=['GET'])
def strava_auth():
    """Initiate Strava OAuth flow"""
    auth_url = strava_service.get_authorization_url()
    return jsonify({"auth_url": auth_url})

@app.route('/api/strava/callback', methods=['GET'])
def strava_callback():
    """Handle Strava OAuth callback"""
    try:
        code = request.args.get('code')
        error = request.args.get('error')
        
        if error:
            print(f"❌ Strava OAuth Error: {error}")
            return jsonify({"error": f"Strava authorization error: {error}"}), 400
        
        if not code:
            print("❌ Strava OAuth: No authorization code provided")
            return jsonify({"error": "Authorization code not provided"}), 400
        
        print(f"✅ Strava OAuth: Received authorization code, exchanging for token...")
        
        # Exchange code for access token
        token_data = strava_service.exchange_code_for_token(code)
        access_token = token_data.get('access_token') if isinstance(token_data, dict) else token_data
        
        if not access_token:
            print("❌ Strava OAuth: Failed to get access token")
            return jsonify({"error": "Failed to obtain access token"}), 500
        
        print(f"✅ Strava OAuth: Successfully obtained access token (expires in {token_data.get('expires_in', 'N/A')} seconds)")
        
        # Validate the token by fetching athlete info
        try:
            athlete_info = strava_service.get_athlete_info(access_token)
            print(f"✅ Strava Connection Validated: Connected as {athlete_info.get('firstname', '')} {athlete_info.get('lastname', '')} (ID: {athlete_info.get('id', 'N/A')})")
        except Exception as validation_error:
            print(f"⚠️  Strava Token Validation Warning: {str(validation_error)}")
            # Continue anyway - token might still work for activities
        
        # Redirect to frontend with token (for MVP simplicity)
        # In production, use secure session management
        return f"""
        <html>
            <body>
                <h2>Successfully authenticated with Strava!</h2>
                <p>You can close this window and return to the app.</p>
                <script>
                    // Pass token to parent window if in iframe, otherwise store in localStorage
                    if (window.opener) {{
                        window.opener.postMessage({{type: 'strava_token', token: '{access_token}'}}, '*');
                        window.close();
                    }} else {{
                        localStorage.setItem('strava_access_token', '{access_token}');
                        window.location.href = 'http://localhost:3000?strava_connected=true';
                    }}
                </script>
            </body>
        </html>
        """
    
    except Exception as e:
        print(f"❌ Strava OAuth Exception: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/strava/validate', methods=['GET'])
def validate_strava_connection():
    """Validate Strava connection and return athlete info"""
    try:
        access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not access_token:
            return jsonify({"error": "Access token required"}), 401
        
        athlete_info = strava_service.get_athlete_info(access_token)
        print(f"✅ Strava Validation: Valid connection for athlete ID {athlete_info.get('id', 'N/A')}")
        
        return jsonify({
            "valid": True,
            "athlete": athlete_info,
            "message": "Strava connection is valid"
        })
    
    except Exception as e:
        print(f"❌ Strava Validation Error: {str(e)}")
        return jsonify({
            "valid": False,
            "error": str(e),
            "message": "Strava connection validation failed"
        }), 401

@app.route('/api/strava/activities', methods=['GET'])
def get_strava_activities():
    """Fetch user activities from Strava"""
    try:
        access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not access_token:
            return jsonify({"error": "Access token required"}), 401
        
        print(f"📊 Fetching Strava activities...")
        activities = strava_service.get_activities(access_token)
        imported_activities.extend(activities)
        
        print(f"✅ Successfully fetched {len(activities)} activities from Strava")
        
        return jsonify({
            "activities": activities,
            "count": len(activities)
        })
    
    except Exception as e:
        print(f"❌ Error fetching Strava activities: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/strava/import', methods=['POST'])
def import_strava_activities():
    """Import selected activities"""
    try:
        data = request.json
        activity_ids = data.get('activity_ids', [])
        
        # In a real app, you'd fetch these from Strava and store them
        imported = [act for act in imported_activities if act.get('id') in activity_ids]
        
        return jsonify({
            "message": f"Imported {len(imported)} activities",
            "activities": imported
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

