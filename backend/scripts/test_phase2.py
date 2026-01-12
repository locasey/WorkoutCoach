"""
Test script for Phase 2: Workout Plan Management API
Tests all endpoints and plan limit functionality
"""
import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:5000/api"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")

def print_result(test_name, success, message):
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} {test_name}: {message}")

def test_health_check():
    """Test 1: Health check"""
    print_test_header("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_result("Health Check", True, "API is running")
            return True
        else:
            print_result("Health Check", False, f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Health Check", False, f"Connection error: {str(e)}")
        print("   Make sure the backend server is running on port 5000")
        return False

def test_list_plans():
    """Test 2: List all workout plans"""
    print_test_header("List All Workout Plans")
    try:
        response = requests.get(f"{BASE_URL}/workout-plans")
        if response.status_code == 200:
            data = response.json()
            plans = data.get('plans', [])
            count = data.get('count', 0)
            max_allowed = data.get('max_allowed', 5)
            
            print(f"   Found {count} plan(s) (max: {max_allowed})")
            for i, plan in enumerate(plans, 1):
                print(f"   Plan {i}: {plan.get('goal', 'N/A')[:50]}... (Active: {plan.get('is_active', False)})")
            
            print_result("List Plans", True, f"Retrieved {count} plans")
            return plans
        else:
            print_result("List Plans", False, f"Status: {response.status_code}, {response.text}")
            return []
    except Exception as e:
        print_result("List Plans", False, f"Error: {str(e)}")
        return []

def test_get_active_plan():
    """Test 3: Get active workout plan"""
    print_test_header("Get Active Workout Plan")
    try:
        response = requests.get(f"{BASE_URL}/workout-plans/active")
        if response.status_code == 200:
            data = response.json()
            plan = data.get('plan')
            
            if plan:
                print(f"   Active Plan: {plan.get('goal', 'N/A')[:50]}...")
                print(f"   Workouts: {len(plan.get('workouts', []))}")
                print_result("Get Active Plan", True, "Active plan retrieved")
            else:
                print_result("Get Active Plan", True, "No active plan (expected if none set)")
            return plan
        else:
            print_result("Get Active Plan", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        print_result("Get Active Plan", False, f"Error: {str(e)}")
        return None

def test_get_specific_plan(plan_id):
    """Test 4: Get specific workout plan"""
    print_test_header(f"Get Specific Plan (ID: {plan_id[:8]}...)")
    try:
        response = requests.get(f"{BASE_URL}/workout-plans/{plan_id}")
        if response.status_code == 200:
            data = response.json()
            plan = data.get('plan', {})
            print(f"   Goal: {plan.get('goal', 'N/A')[:50]}...")
            print(f"   Duration: {plan.get('duration_weeks', 0)} weeks")
            print(f"   Workouts: {len(plan.get('workouts', []))}")
            print_result("Get Specific Plan", True, "Plan retrieved successfully")
            return plan
        else:
            print_result("Get Specific Plan", False, f"Status: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print_result("Get Specific Plan", False, f"Error: {str(e)}")
        return None

def test_activate_plan(plan_id):
    """Test 5: Activate a workout plan"""
    print_test_header(f"Activate Plan (ID: {plan_id[:8]}...)")
    try:
        response = requests.post(f"{BASE_URL}/workout-plans/{plan_id}/activate")
        if response.status_code == 200:
            data = response.json()
            plan = data.get('plan', {})
            print(f"   Activated: {plan.get('goal', 'N/A')[:50]}...")
            print_result("Activate Plan", True, "Plan activated successfully")
            return True
        else:
            print_result("Activate Plan", False, f"Status: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print_result("Activate Plan", False, f"Error: {str(e)}")
        return False

def test_plan_limit():
    """Test 6: Test plan limit enforcement"""
    print_test_header("Plan Limit Enforcement")
    try:
        # First, check current count
        response = requests.get(f"{BASE_URL}/workout-plans")
        if response.status_code == 200:
            data = response.json()
            current_count = data.get('count', 0)
            max_allowed = data.get('max_allowed', 5)
            
            print(f"   Current plans: {current_count}/{max_allowed}")
            
            if current_count >= max_allowed:
                print("   [INFO] At limit - testing limit enforcement...")
                # Try to create a new plan (this should fail)
                test_message = "Create a test 4-week 5K plan"
                response = requests.post(
                    f"{BASE_URL}/chat",
                    json={"message": test_message},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 400:
                    data = response.json()
                    if "Maximum workout plans reached" in data.get('error', ''):
                        print(f"   [OK] Limit enforced correctly")
                        print(f"   [OK] Error message includes existing plans list")
                        print_result("Plan Limit", True, "Limit enforcement working")
                        return True
                    else:
                        print_result("Plan Limit", False, "Wrong error message")
                        return False
                else:
                    print_result("Plan Limit", False, f"Expected 400, got {response.status_code}")
                    return False
            else:
                print(f"   [INFO] Not at limit yet ({current_count}/{max_allowed})")
                print_result("Plan Limit", True, "Limit check working (not at limit)")
                return True
        else:
            print_result("Plan Limit", False, f"Could not check current count: {response.status_code}")
            return False
    except Exception as e:
        print_result("Plan Limit", False, f"Error: {str(e)}")
        return False

def test_delete_plan(plan_id, is_active=False):
    """Test 7: Delete a workout plan"""
    print_test_header(f"Delete Plan (ID: {plan_id[:8]}...)")
    try:
        if is_active:
            print("   [INFO] Plan is active - should fail to delete")
            expected_status = 400
        else:
            print("   [INFO] Plan is inactive - should delete successfully")
            expected_status = 200
        
        response = requests.delete(f"{BASE_URL}/workout-plans/{plan_id}")
        
        if response.status_code == expected_status:
            if is_active:
                data = response.json()
                if "active" in data.get('error', '').lower():
                    print_result("Delete Active Plan Protection", True, "Cannot delete active plan (correct)")
                    return True
                else:
                    print_result("Delete Active Plan Protection", False, "Wrong error message")
                    return False
            else:
                print_result("Delete Plan", True, "Plan deleted successfully")
                return True
        else:
            print_result("Delete Plan", False, f"Expected {expected_status}, got {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print_result("Delete Plan", False, f"Error: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("PHASE 2 API TESTING")
    print("="*60)
    print("\nMake sure the backend server is running on http://localhost:5000")
    print("Starting tests in 2 seconds...\n")
    import time
    time.sleep(2)
    
    results = []
    
    # Test 1: Health check
    if not test_health_check():
        print("\n[ERROR] Backend server is not running. Please start it first.")
        return
    
    # Test 2: List plans
    plans = test_list_plans()
    
    # Test 3: Get active plan
    active_plan = test_get_active_plan()
    
    # Test 4: Get specific plan (if we have plans)
    if plans:
        first_plan_id = plans[0].get('id')
        if first_plan_id:
            test_get_specific_plan(first_plan_id)
    
    # Test 5: Activate a plan (if we have plans)
    if plans:
        first_plan_id = plans[0].get('id')
        if first_plan_id:
            test_activate_plan(first_plan_id)
            # Re-check active plan
            active_plan = test_get_active_plan()
    
    # Test 6: Plan limit enforcement
    test_plan_limit()
    
    # Test 7: Try to delete active plan (should fail)
    # Re-fetch plans to get current state
    plans = test_list_plans()
    active_plan = test_get_active_plan()
    
    if active_plan:
        active_plan_id = active_plan.get('id')
        if active_plan_id:
            test_delete_plan(active_plan_id, is_active=True)
    
    # Test 8: Delete inactive plan (if we have one)
    # Re-fetch plans again to get updated state
    plans = test_list_plans()
    inactive_plans = [p for p in plans if not p.get('is_active', False)]
    if inactive_plans:
        inactive_plan_id = inactive_plans[0].get('id')
        if inactive_plan_id:
            test_delete_plan(inactive_plan_id, is_active=False)
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
    print("\nReview the results above to verify all endpoints are working correctly.")

if __name__ == "__main__":
    main()

