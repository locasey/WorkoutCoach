#!/usr/bin/env python3
"""
Seed database with test data for development.
"""
import sys
import os
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.workout_plan_service import WorkoutPlanService

def create_sample_workout_plan():
    """Create a sample workout plan for testing"""
    db = SessionLocal()
    
    try:
        # Sample workout plan data
        plan_data = {
            "goal": "12-week half marathon training plan",
            "duration_weeks": 12,
            "user_request": "Create a 12-week half marathon training plan",
            "workouts": [
                # Week 1
                {"week": 1, "day": 1, "type": "easy_run", "distance_km": 5.0, "pace": "easy pace", "notes": "Start easy"},
                {"week": 1, "day": 2, "type": "rest", "notes": "Rest day"},
                {"week": 1, "day": 3, "type": "tempo", "distance_km": 6.0, "pace": "tempo pace", "notes": "Tempo run"},
                {"week": 1, "day": 4, "type": "rest", "notes": "Rest day"},
                {"week": 1, "day": 5, "type": "easy_run", "distance_km": 5.0, "pace": "easy pace", "notes": "Easy run"},
                {"week": 1, "day": 6, "type": "rest", "notes": "Rest day"},
                {"week": 1, "day": 7, "type": "long_run", "distance_km": 10.0, "pace": "easy pace", "notes": "Long run"},
                # Week 2
                {"week": 2, "day": 1, "type": "easy_run", "distance_km": 5.0, "pace": "easy pace", "notes": "Easy run"},
                {"week": 2, "day": 2, "type": "rest", "notes": "Rest day"},
                {"week": 2, "day": 3, "type": "intervals", "distance_km": 6.0, "pace": "interval pace", "notes": "4x800m intervals"},
                {"week": 2, "day": 4, "type": "rest", "notes": "Rest day"},
                {"week": 2, "day": 5, "type": "easy_run", "distance_km": 6.0, "pace": "easy pace", "notes": "Easy run"},
                {"week": 2, "day": 6, "type": "rest", "notes": "Rest day"},
                {"week": 2, "day": 7, "type": "long_run", "distance_km": 12.0, "pace": "easy pace", "notes": "Long run"},
            ]
        }
        
        # Create the plan
        workout_plan = WorkoutPlanService.create_workout_plan(
            db=db,
            plan_data=plan_data,
            user_id=None
        )
        
        print(f"✅ Created sample workout plan: {workout_plan.goal}")
        print(f"   Plan ID: {workout_plan.id}")
        print(f"   Duration: {workout_plan.duration_weeks} weeks")
        print(f"   Start Date: {workout_plan.start_date}")
        print(f"   Workouts: {len(workout_plan.workouts)}")
        
        return workout_plan
    
    except Exception as e:
        print(f"❌ Error creating sample plan: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == '__main__':
    print("=" * 50)
    print("Database Seeding Script")
    print("=" * 50)
    
    try:
        create_sample_workout_plan()
        print("\n✅ Database seeding complete!")
    except Exception as e:
        print(f"\n❌ Database seeding failed: {str(e)}")
        sys.exit(1)

