from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import io

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

# In-memory storage (for backward compatibility - will be removed)
workout_plans = {}
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
        
        # Generate workout plan using LLM
        workout_plan_data = llm_service.generate_workout_plan(user_message)
        
        # Save to database
        db = next(get_db())
        try:
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

@app.route('/api/workout-plan/<plan_id>', methods=['GET'])
def get_workout_plan(plan_id):
    """Retrieve a specific workout plan"""
    if plan_id not in workout_plans:
        return jsonify({"error": "Workout plan not found"}), 404
    
    return jsonify({
        "plan_id": plan_id,
        "workout_plan": workout_plans[plan_id]
    })

@app.route('/api/export/excel/<plan_id>', methods=['GET'])
def export_excel(plan_id):
    """Export workout plan to Excel"""
    try:
        if plan_id not in workout_plans:
            return jsonify({"error": "Workout plan not found"}), 404
        
        workout_plan = workout_plans[plan_id]
        excel_file = excel_service.create_workout_plan_excel(workout_plan)
        
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'workout_plan_{plan_id}.xlsx'
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

