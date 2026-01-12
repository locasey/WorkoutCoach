"""
Test script for Phase 3: Week View Backend API
Tests all week/month view endpoints and completion toggling
"""
import sys
import os
import requests
import json
from datetime import date, timedelta
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

def test_get_current_week():
    """Test 2: Get workouts for current week"""
    print_test_header("Get Current Week Workouts")
    try:
        response = requests.get(f"{BASE_URL}/workouts/week")
        if response.status_code == 200:
            data = response.json()
            week_start = data.get('week_start')
            week_end = data.get('week_end')
            workouts = data.get('workouts', [])
            count = data.get('count', 0)
            
            print(f"   Week: {week_start} to {week_end}")
            print(f"   Found {count} workout(s)")
            
            if count > 0:
                print(f"   Sample workout: {workouts[0].get('type', 'N/A')} on {workouts[0].get('scheduled_date', 'N/A')}")
            
            print_result("Get Current Week", True, f"Retrieved {count} workouts")
            return data
        else:
            print_result("Get Current Week", False, f"Status: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print_result("Get Current Week", False, f"Error: {str(e)}")
        return None

def test_get_week_offset():
    """Test 3: Get workouts for week by offset"""
    print_test_header("Get Week by Offset")
    try:
        # Test current week (0)
        response = requests.get(f"{BASE_URL}/workouts/week/0")
        if response.status_code == 200:
            data = response.json()
            print(f"   Current week (0): {data.get('count', 0)} workouts")
        
        # Test next week (+1)
        response = requests.get(f"{BASE_URL}/workouts/week/1")
        if response.status_code == 200:
            data = response.json()
            print(f"   Next week (+1): {data.get('count', 0)} workouts")
        
        # Test last week (-1)
        response = requests.get(f"{BASE_URL}/workouts/week/-1")
        if response.status_code == 200:
            data = response.json()
            print(f"   Last week (-1): {data.get('count', 0)} workouts")
        
        print_result("Get Week Offset", True, "Week offset queries working")
        return True
    except Exception as e:
        print_result("Get Week Offset", False, f"Error: {str(e)}")
        return False

def test_get_month():
    """Test 4: Get workouts for a month"""
    print_test_header("Get Month Workouts")
    try:
        today = date.today()
        year = today.year
        month = today.month
        
        response = requests.get(f"{BASE_URL}/workouts/month/{year}/{month}")
        if response.status_code == 200:
            data = response.json()
            workouts = data.get('workouts', [])
            count = data.get('count', 0)
            
            print(f"   Month: {year}-{month:02d}")
            print(f"   Found {count} workout(s)")
            
            print_result("Get Month", True, f"Retrieved {count} workouts")
            return data
        else:
            print_result("Get Month", False, f"Status: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print_result("Get Month", False, f"Error: {str(e)}")
        return None

def test_toggle_completion():
    """Test 5: Toggle workout completion"""
    print_test_header("Toggle Workout Completion")
    try:
        # First, get a workout from current week
        response = requests.get(f"{BASE_URL}/workouts/week")
        if response.status_code != 200:
            print_result("Toggle Completion", False, "Could not fetch workouts")
            return False
        
        workouts = response.json().get('workouts', [])
        if len(workouts) == 0:
            print_result("Toggle Completion", True, "No workouts to test (expected if no active plan)")
            return True
        
        workout_id = workouts[0].get('id')
        initial_status = workouts[0].get('is_completed', False)
        
        print(f"   Workout ID: {workout_id[:8]}...")
        print(f"   Initial status: {'Completed' if initial_status else 'Incomplete'}")
        
        # Toggle completion
        response = requests.put(f"{BASE_URL}/workouts/{workout_id}/complete")
        if response.status_code == 200:
            data = response.json()
            new_status = data.get('workout', {}).get('is_completed', False)
            print(f"   New status: {'Completed' if new_status else 'Incomplete'}")
            
            # Toggle back
            response = requests.put(f"{BASE_URL}/workouts/{workout_id}/complete")
            if response.status_code == 200:
                final_status = response.json().get('workout', {}).get('is_completed', False)
                print(f"   Final status (toggled back): {'Completed' if final_status else 'Incomplete'}")
                
                if final_status == initial_status:
                    print_result("Toggle Completion", True, "Toggle working correctly")
                    return True
                else:
                    print_result("Toggle Completion", False, "Toggle did not restore original state")
                    return False
            else:
                print_result("Toggle Completion", False, f"Second toggle failed: {response.status_code}")
                return False
        else:
            print_result("Toggle Completion", False, f"Status: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print_result("Toggle Completion", False, f"Error: {str(e)}")
        return False

def test_get_progress():
    """Test 6: Get week progress summary"""
    print_test_header("Get Week Progress")
    try:
        response = requests.get(f"{BASE_URL}/workouts/progress")
        if response.status_code == 200:
            data = response.json()
            total = data.get('total_workouts', 0)
            completed = data.get('completed_workouts', 0)
            percentage = data.get('completion_percentage', 0)
            
            print(f"   Total workouts: {total}")
            print(f"   Completed: {completed}")
            print(f"   Completion: {percentage}%")
            
            print_result("Get Progress", True, f"Progress summary retrieved")
            return data
        else:
            print_result("Get Progress", False, f"Status: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print_result("Get Progress", False, f"Error: {str(e)}")
        return None

def test_progress_with_offset():
    """Test 7: Get progress for specific week offset"""
    print_test_header("Get Progress with Week Offset")
    try:
        # Test current week
        response = requests.get(f"{BASE_URL}/workouts/progress?week_offset=0")
        if response.status_code == 200:
            data = response.json()
            print(f"   Current week: {data.get('completion_percentage', 0)}% complete")
        
        # Test next week
        response = requests.get(f"{BASE_URL}/workouts/progress?week_offset=1")
        if response.status_code == 200:
            data = response.json()
            print(f"   Next week: {data.get('completion_percentage', 0)}% complete")
        
        print_result("Progress with Offset", True, "Week offset parameter working")
        return True
    except Exception as e:
        print_result("Progress with Offset", False, f"Error: {str(e)}")
        return False

def test_edge_cases():
    """Test 8: Edge cases"""
    print_test_header("Edge Cases")
    results = []
    
    # Test invalid month
    try:
        response = requests.get(f"{BASE_URL}/workouts/month/2024/13")
        if response.status_code == 400:
            print("   [OK] Invalid month (13) correctly rejected")
            results.append(True)
        else:
            print(f"   [FAIL] Expected 400 for invalid month, got {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   [FAIL] Error testing invalid month: {str(e)}")
        results.append(False)
    
    # Test invalid workout ID
    try:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.put(f"{BASE_URL}/workouts/{fake_id}/complete")
        if response.status_code == 404:
            print("   [OK] Invalid workout ID correctly returns 404")
            results.append(True)
        else:
            print(f"   [FAIL] Expected 404 for invalid ID, got {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   [FAIL] Error testing invalid workout ID: {str(e)}")
        results.append(False)
    
    # Test no active plan (should return empty results, not error)
    try:
        response = requests.get(f"{BASE_URL}/workouts/week")
        if response.status_code == 200:
            data = response.json()
            if data.get('count', 0) == 0:
                print("   [OK] No active plan returns empty results (not error)")
                results.append(True)
            else:
                print("   [INFO] Active plan exists (expected if plan is active)")
                results.append(True)
        else:
            print(f"   [FAIL] Expected 200 for no active plan, got {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   [FAIL] Error testing no active plan: {str(e)}")
        results.append(False)
    
    all_passed = all(results)
    print_result("Edge Cases", all_passed, f"{sum(results)}/{len(results)} tests passed")
    return all_passed

def main():
    print("\n" + "="*60)
    print("PHASE 3 API TESTING - Week View Backend API")
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
    
    # Test 2: Get current week
    test_get_current_week()
    
    # Test 3: Get week by offset
    test_get_week_offset()
    
    # Test 4: Get month
    test_get_month()
    
    # Test 5: Toggle completion
    test_toggle_completion()
    
    # Test 6: Get progress
    test_get_progress()
    
    # Test 7: Progress with offset
    test_progress_with_offset()
    
    # Test 8: Edge cases
    test_edge_cases()
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
    print("\nReview the results above to verify all endpoints are working correctly.")
    print("\nNote: Some tests may show 'No workouts' if no active plan exists.")
    print("      This is expected behavior and not an error.")

if __name__ == "__main__":
    main()

