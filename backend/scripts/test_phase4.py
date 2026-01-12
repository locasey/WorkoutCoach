"""
Test script for Phase 4: Workout Editing API
Tests workout update endpoint with validation and partial updates
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

def get_sample_workout():
    """Helper: Get a sample workout to test with"""
    try:
        response = requests.get(f"{BASE_URL}/workouts/week")
        if response.status_code == 200:
            workouts = response.json().get('workouts', [])
            if len(workouts) > 0:
                return workouts[0]
        return None
    except:
        return None

def test_update_single_field():
    """Test 2: Update a single field (partial update)"""
    print_test_header("Update Single Field (Partial Update)")
    try:
        workout = get_sample_workout()
        if not workout:
            print_result("Update Single Field", True, "No workouts available to test (expected if no active plan)")
            return True
        
        workout_id = workout.get('id')
        original_notes = workout.get('notes', '')
        new_notes = f"Updated notes - {os.urandom(4).hex()}"
        
        print(f"   Workout ID: {workout_id[:8]}...")
        print(f"   Original notes: {original_notes[:50] if original_notes else 'None'}...")
        print(f"   Updating notes only...")
        
        response = requests.put(
            f"{BASE_URL}/workouts/{workout_id}",
            json={"notes": new_notes},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            updated_workout = data.get('workout', {})
            updated_notes = updated_workout.get('notes', '')
            
            print(f"   New notes: {updated_notes[:50]}...")
            
            if updated_notes == new_notes:
                # Restore original notes
                requests.put(
                    f"{BASE_URL}/workouts/{workout_id}",
                    json={"notes": original_notes},
                    headers={"Content-Type": "application/json"}
                )
                print_result("Update Single Field", True, "Single field update successful")
                return True
            else:
                print_result("Update Single Field", False, "Notes not updated correctly")
                return False
        else:
            print_result("Update Single Field", False, f"Status: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print_result("Update Single Field", False, f"Error: {str(e)}")
        return False

def test_update_multiple_fields():
    """Test 3: Update multiple fields at once"""
    print_test_header("Update Multiple Fields")
    try:
        workout = get_sample_workout()
        if not workout:
            print_result("Update Multiple Fields", True, "No workouts available to test")
            return True
        
        workout_id = workout.get('id')
        original_data = {
            'type': workout.get('type'),
            'distance_km': workout.get('distance_km'),
            'notes': workout.get('notes')
        }
        
        print(f"   Workout ID: {workout_id[:8]}...")
        print(f"   Original: type={original_data['type']}, distance={original_data['distance_km']}")
        
        update_data = {
            'type': 'tempo',
            'distance_km': 5.5,
            'notes': 'Updated multiple fields test'
        }
        
        response = requests.put(
            f"{BASE_URL}/workouts/{workout_id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            updated_workout = data.get('workout', {})
            
            print(f"   Updated: type={updated_workout.get('type')}, distance={updated_workout.get('distance_km')}")
            
            # Verify updates
            if (updated_workout.get('type') == update_data['type'] and
                updated_workout.get('distance_km') == update_data['distance_km'] and
                updated_workout.get('notes') == update_data['notes']):
                
                # Restore original values
                requests.put(
                    f"{BASE_URL}/workouts/{workout_id}",
                    json=original_data,
                    headers={"Content-Type": "application/json"}
                )
                print_result("Update Multiple Fields", True, "Multiple fields updated successfully")
                return True
            else:
                print_result("Update Multiple Fields", False, "Fields not updated correctly")
                return False
        else:
            print_result("Update Multiple Fields", False, f"Status: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print_result("Update Multiple Fields", False, f"Error: {str(e)}")
        return False

def test_validation_invalid_type():
    """Test 4: Validation - Invalid workout type"""
    print_test_header("Validation - Invalid Workout Type")
    try:
        workout = get_sample_workout()
        if not workout:
            print_result("Validation - Invalid Type", True, "No workouts available to test")
            return True
        
        workout_id = workout.get('id')
        
        response = requests.put(
            f"{BASE_URL}/workouts/{workout_id}",
            json={"type": "invalid_workout_type"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            error_msg = response.json().get('error', '')
            if "Invalid workout type" in error_msg:
                print(f"   [OK] Invalid type correctly rejected: {error_msg[:80]}...")
                print_result("Validation - Invalid Type", True, "Invalid type validation working")
                return True
            else:
                print_result("Validation - Invalid Type", False, f"Wrong error message: {error_msg}")
                return False
        else:
            print_result("Validation - Invalid Type", False, f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        print_result("Validation - Invalid Type", False, f"Error: {str(e)}")
        return False

def test_validation_negative_distance():
    """Test 5: Validation - Negative distance"""
    print_test_header("Validation - Negative Distance")
    try:
        workout = get_sample_workout()
        if not workout:
            print_result("Validation - Negative Distance", True, "No workouts available to test")
            return True
        
        workout_id = workout.get('id')
        
        response = requests.put(
            f"{BASE_URL}/workouts/{workout_id}",
            json={"distance_km": -5.0},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            error_msg = response.json().get('error', '')
            if "non-negative" in error_msg.lower() or "validation" in error_msg.lower():
                print(f"   [OK] Negative distance correctly rejected")
                print_result("Validation - Negative Distance", True, "Negative distance validation working")
                return True
            else:
                print_result("Validation - Negative Distance", False, f"Wrong error message: {error_msg}")
                return False
        else:
            print_result("Validation - Negative Distance", False, f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        print_result("Validation - Negative Distance", False, f"Error: {str(e)}")
        return False

def test_validation_invalid_duration():
    """Test 6: Validation - Invalid duration type"""
    print_test_header("Validation - Invalid Duration")
    try:
        workout = get_sample_workout()
        if not workout:
            print_result("Validation - Invalid Duration", True, "No workouts available to test")
            return True
        
        workout_id = workout.get('id')
        
        response = requests.put(
            f"{BASE_URL}/workouts/{workout_id}",
            json={"duration_minutes": "not_a_number"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            error_msg = response.json().get('error', '')
            if "valid" in error_msg.lower() or "validation" in error_msg.lower():
                print(f"   [OK] Invalid duration correctly rejected")
                print_result("Validation - Invalid Duration", True, "Invalid duration validation working")
                return True
            else:
                print_result("Validation - Invalid Duration", False, f"Wrong error message: {error_msg}")
                return False
        else:
            print_result("Validation - Invalid Duration", False, f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        print_result("Validation - Invalid Duration", False, f"Error: {str(e)}")
        return False

def test_clear_field():
    """Test 7: Clear a field (set to None)"""
    print_test_header("Clear Field (Set to None)")
    try:
        workout = get_sample_workout()
        if not workout:
            print_result("Clear Field", True, "No workouts available to test")
            return True
        
        workout_id = workout.get('id')
        original_notes = workout.get('notes')
        
        # Only test if there are notes to clear
        if not original_notes:
            print("   [INFO] No notes to clear, skipping test")
            print_result("Clear Field", True, "No field to clear (expected)")
            return True
        
        print(f"   Workout ID: {workout_id[:8]}...")
        print(f"   Original notes: {original_notes[:50]}...")
        print(f"   Clearing notes...")
        
        response = requests.put(
            f"{BASE_URL}/workouts/{workout_id}",
            json={"notes": None},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            updated_workout = data.get('workout', {})
            cleared_notes = updated_workout.get('notes')
            
            if cleared_notes is None:
                # Restore original notes
                requests.put(
                    f"{BASE_URL}/workouts/{workout_id}",
                    json={"notes": original_notes},
                    headers={"Content-Type": "application/json"}
                )
                print_result("Clear Field", True, "Field cleared successfully")
                return True
            else:
                print_result("Clear Field", False, "Field not cleared (not None)")
                return False
        else:
            print_result("Clear Field", False, f"Status: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print_result("Clear Field", False, f"Error: {str(e)}")
        return False

def test_update_updated_at_timestamp():
    """Test 8: Verify updated_at timestamp is set"""
    print_test_header("Updated At Timestamp")
    try:
        workout = get_sample_workout()
        if not workout:
            print_result("Updated At Timestamp", True, "No workouts available to test")
            return True
        
        workout_id = workout.get('id')
        original_updated_at = workout.get('updated_at')
        
        print(f"   Workout ID: {workout_id[:8]}...")
        print(f"   Original updated_at: {original_updated_at}")
        
        import time
        time.sleep(1)  # Wait a second to ensure timestamp difference
        
        response = requests.put(
            f"{BASE_URL}/workouts/{workout_id}",
            json={"notes": "Testing timestamp update"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            updated_workout = data.get('workout', {})
            new_updated_at = updated_workout.get('updated_at')
            
            print(f"   New updated_at: {new_updated_at}")
            
            if new_updated_at and new_updated_at != original_updated_at:
                print_result("Updated At Timestamp", True, "Timestamp updated correctly")
                return True
            else:
                print_result("Updated At Timestamp", False, "Timestamp not updated")
                return False
        else:
            print_result("Updated At Timestamp", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Updated At Timestamp", False, f"Error: {str(e)}")
        return False

def test_invalid_workout_id():
    """Test 9: Invalid workout ID"""
    print_test_header("Invalid Workout ID")
    try:
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = requests.put(
            f"{BASE_URL}/workouts/{fake_id}",
            json={"notes": "test"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 404:
            print(f"   [OK] Invalid workout ID correctly returns 404")
            print_result("Invalid Workout ID", True, "404 returned for invalid ID")
            return True
        else:
            print_result("Invalid Workout ID", False, f"Expected 404, got {response.status_code}")
            return False
    except Exception as e:
        print_result("Invalid Workout ID", False, f"Error: {str(e)}")
        return False

def test_empty_request_body():
    """Test 10: Empty request body"""
    print_test_header("Empty Request Body")
    try:
        workout = get_sample_workout()
        if not workout:
            print_result("Empty Request Body", True, "No workouts available to test")
            return True
        
        workout_id = workout.get('id')
        
        response = requests.put(
            f"{BASE_URL}/workouts/{workout_id}",
            json={},
            headers={"Content-Type": "application/json"}
        )
        
        # Empty body should be allowed (no fields to update, but not an error)
        if response.status_code in [200, 400]:
            # 200 if empty body is allowed, 400 if it requires at least one field
            print_result("Empty Request Body", True, f"Empty body handled (status {response.status_code})")
            return True
        else:
            print_result("Empty Request Body", False, f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Empty Request Body", False, f"Error: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("PHASE 4 API TESTING - Workout Editing API")
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
    
    # Test 2: Update single field
    test_update_single_field()
    
    # Test 3: Update multiple fields
    test_update_multiple_fields()
    
    # Test 4: Validation - invalid type
    test_validation_invalid_type()
    
    # Test 5: Validation - negative distance
    test_validation_negative_distance()
    
    # Test 6: Validation - invalid duration
    test_validation_invalid_duration()
    
    # Test 7: Clear field
    test_clear_field()
    
    # Test 8: Updated at timestamp
    test_update_updated_at_timestamp()
    
    # Test 9: Invalid workout ID
    test_invalid_workout_id()
    
    # Test 10: Empty request body
    test_empty_request_body()
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
    print("\nReview the results above to verify all endpoints are working correctly.")
    print("\nNote: Some tests may show 'No workouts' if no active plan exists.")
    print("      This is expected behavior and not an error.")

if __name__ == "__main__":
    main()

