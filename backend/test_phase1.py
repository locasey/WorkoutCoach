#!/usr/bin/env python3
"""
Comprehensive test script for Phase 1: Database Foundation & Setup
Tests all components implemented in Phase 1.
"""
import sys
import os
from datetime import date, datetime, timedelta
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, init_db, get_db
from models.workout_plan import WorkoutPlan
from models.workout import Workout
from services.workout_plan_service import WorkoutPlanService
import uuid

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def print_test_header(test_name):
    """Print formatted test header"""
    print("\n" + "=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)

def print_result(test_name, passed, message=""):
    """Track and print test result"""
    if passed:
        test_results["passed"].append(test_name)
        print(f"✅ PASS: {test_name}")
        if message:
            print(f"   {message}")
    else:
        test_results["failed"].append(test_name)
        print(f"❌ FAIL: {test_name}")
        if message:
            print(f"   {message}")

def print_warning(message):
    """Print warning message"""
    test_results["warnings"].append(message)
    print(f"⚠️  WARNING: {message}")

def test_database_connection():
    """Test 1: Database connection"""
    print_test_header("Database Connection")
    try:
        # Try to connect to database
        conn = engine.connect()
        conn.close()
        print_result("Database Connection", True, "Successfully connected to PostgreSQL")
        return True
    except Exception as e:
        print_result("Database Connection", False, f"Failed to connect: {str(e)}")
        print("   Make sure PostgreSQL is running (docker-compose up -d)")
        return False

def test_database_initialization():
    """Test 2: Database table creation"""
    print_test_header("Database Initialization")
    try:
        # Initialize database (create tables)
        init_db()
        print_result("Database Initialization", True, "Tables created successfully")
        
        # Verify tables exist by trying to query them
        db = SessionLocal()
        try:
            # Try to query workout_plans table
            count = db.query(WorkoutPlan).count()
            print(f"   Found {count} workout plans in database")
            print_result("Table Verification", True, "workout_plans table exists and is queryable")
            
            # Try to query workouts table
            workout_count = db.query(Workout).count()
            print(f"   Found {workout_count} workouts in database")
            print_result("Workouts Table Verification", True, "workouts table exists and is queryable")
            
            return True
        finally:
            db.close()
    except Exception as e:
        print_result("Database Initialization", False, f"Failed: {str(e)}")
        return False

def test_workout_plan_creation():
    """Test 3: Create workout plan via service"""
    print_test_header("Workout Plan Creation (Service Layer)")
    db = SessionLocal()
    try:
        # Sample workout plan data
        plan_data = {
            "goal": "Test 4-week 5K training plan",
            "duration_weeks": 4,
            "user_request": "Create a test 4-week 5K training plan",
            "workouts": [
                {"week": 1, "day": 1, "type": "easy_run", "distance_km": 3.0, "pace": "easy", "notes": "Test run 1"},
                {"week": 1, "day": 3, "type": "tempo", "distance_km": 4.0, "pace": "tempo", "notes": "Test tempo"},
                {"week": 1, "day": 5, "type": "easy_run", "distance_km": 3.0, "pace": "easy", "notes": "Test run 2"},
                {"week": 1, "day": 7, "type": "long_run", "distance_km": 5.0, "pace": "easy", "notes": "Test long run"},
            ]
        }
        
        # Create workout plan
        workout_plan = WorkoutPlanService.create_workout_plan(
            db=db,
            plan_data=plan_data,
            user_id=None
        )
        
        # Verify plan was created
        assert workout_plan is not None, "Workout plan should not be None"
        assert workout_plan.id is not None, "Workout plan should have an ID"
        assert workout_plan.goal == plan_data["goal"], "Goal should match"
        assert workout_plan.duration_weeks == plan_data["duration_weeks"], "Duration should match"
        assert workout_plan.start_date is not None, "Start date should be set"
        assert len(workout_plan.workouts) == 4, f"Should have 4 workouts, got {len(workout_plan.workouts)}"
        
        print(f"   Plan ID: {workout_plan.id}")
        print(f"   Goal: {workout_plan.goal}")
        print(f"   Start Date: {workout_plan.start_date}")
        print(f"   Workouts Created: {len(workout_plan.workouts)}")
        
        # Verify workouts
        for i, workout in enumerate(workout_plan.workouts):
            assert workout.workout_plan_id == workout_plan.id, f"Workout {i} should be linked to plan"
            assert workout.scheduled_date is not None, f"Workout {i} should have scheduled_date"
            print(f"   Workout {i+1}: {workout.type} on {workout.scheduled_date} ({workout.distance_km}km)")
        
        print_result("Workout Plan Creation", True, "Plan and workouts created successfully")
        return workout_plan.id
    except Exception as e:
        print_result("Workout Plan Creation", False, f"Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def test_workout_plan_retrieval(plan_id):
    """Test 4: Retrieve workout plan from database"""
    print_test_header("Workout Plan Retrieval")
    if plan_id is None:
        print_warning("Skipping retrieval test - no plan ID available")
        return False
    
    db = SessionLocal()
    try:
        # Retrieve plan by ID
        workout_plan = WorkoutPlanService.get_workout_plan(db, plan_id)
        
        assert workout_plan is not None, "Workout plan should be retrievable"
        assert workout_plan.id == plan_id, "Plan ID should match"
        assert len(workout_plan.workouts) == 4, f"Should have 4 workouts, got {len(workout_plan.workouts)}"
        
        print(f"   Retrieved Plan ID: {workout_plan.id}")
        print(f"   Goal: {workout_plan.goal}")
        print(f"   Workouts: {len(workout_plan.workouts)}")
        
        # Test to_dict method
        plan_dict = workout_plan.to_dict()
        assert plan_dict["id"] == str(plan_id), "Dict ID should match"
        assert "workouts" not in plan_dict, "to_dict should not include workouts by default"
        
        print_result("Workout Plan Retrieval", True, "Plan retrieved successfully")
        return True
    except Exception as e:
        print_result("Workout Plan Retrieval", False, f"Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_get_all_plans():
    """Test 5: Get all workout plans"""
    print_test_header("Get All Workout Plans")
    db = SessionLocal()
    try:
        plans = WorkoutPlanService.get_all_workout_plans(db, user_id=None)
        
        assert isinstance(plans, list), "Should return a list"
        print(f"   Found {len(plans)} workout plan(s)")
        
        for plan in plans:
            print(f"   - {plan.goal} (ID: {plan.id}, Active: {plan.is_active})")
        
        print_result("Get All Plans", True, f"Retrieved {len(plans)} plan(s)")
        return True
    except Exception as e:
        print_result("Get All Plans", False, f"Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_active_plan_management():
    """Test 6: Active plan management"""
    print_test_header("Active Plan Management")
    db = SessionLocal()
    try:
        # Get all plans
        all_plans = WorkoutPlanService.get_all_workout_plans(db, user_id=None)
        if len(all_plans) == 0:
            print_warning("No plans available for active plan testing")
            return False
        
        # Get first plan
        test_plan = all_plans[0]
        plan_id = test_plan.id
        
        # Set as active
        active_plan = WorkoutPlanService.set_active_workout_plan(db, plan_id, user_id=None)
        assert active_plan.is_active == True, "Plan should be active"
        print(f"   Set plan {plan_id} as active")
        
        # Verify no other plans are active
        other_plans = [p for p in all_plans if p.id != plan_id]
        for plan in other_plans:
            db.refresh(plan)
            if plan.is_active:
                print_warning(f"Plan {plan.id} is still active (should be deactivated)")
        
        # Get active plan
        retrieved_active = WorkoutPlanService.get_active_workout_plan(db, user_id=None)
        assert retrieved_active is not None, "Should have an active plan"
        assert retrieved_active.id == plan_id, "Active plan ID should match"
        
        print(f"   Active plan: {retrieved_active.goal}")
        print_result("Active Plan Management", True, "Active plan set and retrieved successfully")
        return True
    except Exception as e:
        print_result("Active Plan Management", False, f"Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_scheduled_date_calculation():
    """Test 7: Verify scheduled_date calculation"""
    print_test_header("Scheduled Date Calculation")
    db = SessionLocal()
    try:
        # Get a plan with workouts
        plans = WorkoutPlanService.get_all_workout_plans(db, user_id=None)
        if len(plans) == 0:
            print_warning("No plans available for date calculation testing")
            return False
        
        plan = plans[0]
        if len(plan.workouts) == 0:
            print_warning("Plan has no workouts for date calculation testing")
            return False
        
        # Verify scheduled dates
        start_date = plan.start_date
        print(f"   Plan start date: {start_date}")
        
        for workout in plan.workouts[:3]:  # Check first 3 workouts
            expected_date = start_date + timedelta(days=(workout.week - 1) * 7 + (workout.day - 1))
            actual_date = workout.scheduled_date
            
            print(f"   Week {workout.week}, Day {workout.day}: Expected {expected_date}, Got {actual_date}")
            assert actual_date == expected_date, f"Date mismatch for workout {workout.id}"
        
        print_result("Scheduled Date Calculation", True, "All scheduled dates calculated correctly")
        return True
    except Exception as e:
        print_result("Scheduled Date Calculation", False, f"Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_workout_completion_toggle():
    """Test 8: Toggle workout completion"""
    print_test_header("Workout Completion Toggle")
    db = SessionLocal()
    try:
        # Get a workout
        workouts = db.query(Workout).limit(1).all()
        if len(workouts) == 0:
            print_warning("No workouts available for completion testing")
            return False
        
        workout = workouts[0]
        initial_status = workout.is_completed
        
        # Toggle completion
        updated_workout = WorkoutPlanService.toggle_workout_completion(db, workout.id)
        assert updated_workout.is_completed != initial_status, "Completion status should toggle"
        
        if updated_workout.is_completed:
            assert updated_workout.completed_at is not None, "completed_at should be set when completed"
            print(f"   Workout {workout.id} marked as completed at {updated_workout.completed_at}")
        else:
            assert updated_workout.completed_at is None, "completed_at should be None when not completed"
            print(f"   Workout {workout.id} marked as not completed")
        
        # Toggle back
        WorkoutPlanService.toggle_workout_completion(db, workout.id)
        
        print_result("Workout Completion Toggle", True, "Completion toggle works correctly")
        return True
    except Exception as e:
        print_result("Workout Completion Toggle", False, f"Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_data_persistence():
    """Test 9: Data persistence across sessions"""
    print_test_header("Data Persistence")
    try:
        # Create a plan in one session
        db1 = SessionLocal()
        plan_data = {
            "goal": "Persistence Test Plan",
            "duration_weeks": 2,
            "user_request": "Test persistence",
            "workouts": [
                {"week": 1, "day": 1, "type": "easy_run", "distance_km": 5.0}
            ]
        }
        workout_plan = WorkoutPlanService.create_workout_plan(db1, plan_data, user_id=None)
        plan_id = workout_plan.id
        db1.close()
        
        # Retrieve in a new session
        db2 = SessionLocal()
        retrieved_plan = WorkoutPlanService.get_workout_plan(db2, plan_id)
        assert retrieved_plan is not None, "Plan should persist across sessions"
        assert retrieved_plan.goal == plan_data["goal"], "Plan data should persist"
        db2.close()
        
        print(f"   Created plan {plan_id} in session 1")
        print(f"   Retrieved plan {plan_id} in session 2")
        print_result("Data Persistence", True, "Data persists across database sessions")
        return True
    except Exception as e:
        print_result("Data Persistence", False, f"Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def print_summary():
    """Print test summary"""
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {len(test_results['passed'])}")
    print(f"❌ Failed: {len(test_results['failed'])}")
    print(f"⚠️  Warnings: {len(test_results['warnings'])}")
    
    if test_results['failed']:
        print("\nFailed Tests:")
        for test in test_results['failed']:
            print(f"  - {test}")
    
    if test_results['warnings']:
        print("\nWarnings:")
        for warning in test_results['warnings']:
            print(f"  - {warning}")
    
    print("\n" + "=" * 70)
    
    if len(test_results['failed']) == 0:
        print("🎉 All tests passed! Phase 1 implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("PHASE 1 TEST SUITE: Database Foundation & Setup")
    print("=" * 70)
    
    # Run tests in sequence
    if not test_database_connection():
        print("\n❌ Cannot proceed without database connection. Please start PostgreSQL.")
        return False
    
    if not test_database_initialization():
        print("\n❌ Database initialization failed. Cannot proceed.")
        return False
    
    plan_id = test_workout_plan_creation()
    test_workout_plan_retrieval(plan_id)
    test_get_all_plans()
    test_active_plan_management()
    test_scheduled_date_calculation()
    test_workout_completion_toggle()
    test_data_persistence()
    
    # Print summary
    return print_summary()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

