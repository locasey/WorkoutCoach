"""
Simple script to check if workout plans are saved in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.workout_plan_service import WorkoutPlanService
from models.workout_plan import WorkoutPlan
from models.workout import Workout

def check_database():
    """Check what's in the database"""
    db = SessionLocal()
    try:
        # Get all workout plans
        plans = WorkoutPlanService.get_all_workout_plans(db)
        
        print("=" * 60)
        print("DATABASE CHECK - Workout Plans")
        print("=" * 60)
        
        if not plans:
            print("[X] No workout plans found in database")
            print("\nThis could mean:")
            print("  - No plans have been created yet")
            print("  - Plans are being saved to in-memory storage instead")
            print("  - Database connection issue")
        else:
            print(f"[OK] Found {len(plans)} workout plan(s) in database:\n")
            
            for i, plan in enumerate(plans, 1):
                print(f"Plan {i}:")
                print(f"  ID: {plan.id}")
                print(f"  Goal: {plan.goal}")
                print(f"  Duration: {plan.duration_weeks} weeks")
                print(f"  Start Date: {plan.start_date}")
                print(f"  Created: {plan.created_at}")
                print(f"  Active: {'[YES]' if plan.is_active else '[NO]'}")
                print(f"  Workouts: {len(plan.workouts)}")
                
                # Show first few workouts
                if plan.workouts:
                    print(f"  Sample workouts:")
                    for workout in plan.workouts[:3]:
                        print(f"    - {workout.type} on {workout.scheduled_date} ({workout.distance_km}km)" if workout.distance_km else f"    - {workout.type} on {workout.scheduled_date}")
                    if len(plan.workouts) > 3:
                        print(f"    ... and {len(plan.workouts) - 3} more")
                print()
        
        # Count total workouts
        total_workouts = db.query(Workout).count()
        print(f"Total workouts in database: {total_workouts}")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] Error checking database: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_database()

