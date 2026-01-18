# Phase 4 Implementation: Workout Editing API

## Overview

Phase 4 implements the backend API endpoint for manually editing workout details. This allows users to update workout information such as type, distance, pace, and notes after a plan has been created.

## API Endpoint

### Update Workout
**Endpoint**: `PUT /api/workouts/<workout_id>`

**Description**: Updates workout details. Supports partial updates (only provided fields are updated).

**Request Body** (all fields optional):
```json
{
  "type": "tempo",
  "distance_km": 5.5,
  "duration_minutes": 30,
  "pace": "5:00/km",
  "notes": "Updated workout notes"
}
```

**Response**:
```json
{
  "workout": {
    "id": "...",
    "type": "tempo",
    "distance_km": 5.5,
    "duration_minutes": 30,
    "pace": "5:00/km",
    "notes": "Updated workout notes",
    "updated_at": "2026-01-10T23:18:12.778354+00:00",
    ...
  },
  "message": "Workout updated successfully"
}
```

**Error Responses**:
- `400`: Validation errors (invalid field values)
- `404`: Workout not found
- `400`: Invalid workout ID format

## Validation Rules

### Workout Type
- Must be one of: `long_run`, `tempo`, `intervals`, `easy_run`, `rest`, `cross_training`, `recovery`, `fartlek`, `hill_repeats`
- Case-insensitive matching
- Must be a non-empty string

### Distance (distance_km)
- Must be a valid number (float)
- Must be non-negative (>= 0)
- Can be `null` to clear the field

### Duration (duration_minutes)
- Must be a valid integer
- Must be non-negative (>= 0)
- Can be `null` to clear the field

### Pace
- Must be a string if provided
- Can be `null` or empty string to clear the field

### Notes
- Must be a string if provided
- Can be `null` or empty string to clear the field

## Partial Updates

The endpoint supports partial updates - you only need to include the fields you want to update:

```json
// Update only notes
PUT /api/workouts/{id}
{
  "notes": "New notes"
}

// Update type and distance
PUT /api/workouts/{id}
{
  "type": "tempo",
  "distance_km": 6.0
}
```

## Clearing Fields

Fields can be cleared by setting them to `null`:

```json
{
  "notes": null,
  "pace": null
}
```

## Updated At Timestamp

The `updated_at` field is automatically updated by SQLAlchemy whenever any field is modified. This is handled by the `onupdate=func.now()` configuration in the Workout model.

## Service Layer

### New Method: `update_workout()`

**Location**: `WorkoutPlanService.update_workout()`

**Parameters**:
- `db`: Database session
- `workout_id`: UUID of workout to update
- `update_data`: Dictionary with fields to update

**Returns**: Updated `Workout` object

**Raises**: `ValueError` if workout not found or validation fails

### Validation Method: `_validate_workout_data()`

**Location**: `WorkoutPlanService._validate_workout_data()`

Validates all workout fields and returns a dictionary of errors (empty if valid).

### Workout Type Validation: `_validate_workout_type()`

**Location**: `WorkoutPlanService._validate_workout_type()`

Checks if a workout type is in the allowed list.

## Behavior Notes

- **Partial Updates**: Only fields provided in the request body are updated
- **Field Clearing**: Fields can be set to `null` to clear them
- **Automatic Timestamps**: `updated_at` is automatically set by SQLAlchemy
- **Immutable Fields**: `id`, `workout_plan_id`, `week`, `day`, `scheduled_date`, `created_at` cannot be updated via this endpoint
- **Completion Status**: Use the separate `/api/workouts/{id}/complete` endpoint to toggle completion

## Testing

Test script: `backend/scripts/test_phase4.py`

**Test Coverage**:
- ✅ Single field partial update
- ✅ Multiple fields update
- ✅ Invalid workout type validation
- ✅ Negative distance validation
- ✅ Invalid duration validation
- ✅ Field clearing (set to None)
- ✅ Updated_at timestamp tracking
- ✅ Invalid workout ID handling
- ✅ Empty request body handling

**Run Tests**:
```bash
cd backend
python scripts/test_phase4.py
```

## Example Usage

### Update workout notes
```bash
curl -X PUT http://localhost:5000/api/workouts/{workout_id} \
  -H "Content-Type: application/json" \
  -d '{"notes": "Focus on maintaining steady pace"}'
```

### Update multiple fields
```bash
curl -X PUT http://localhost:5000/api/workouts/{workout_id} \
  -H "Content-Type: application/json" \
  -d '{
    "type": "tempo",
    "distance_km": 6.0,
    "pace": "4:30/km",
    "notes": "Tempo run at threshold pace"
  }'
```

### Clear a field
```bash
curl -X PUT http://localhost:5000/api/workouts/{workout_id} \
  -H "Content-Type: application/json" \
  -d '{"notes": null}'
```

## Next Steps

Phase 4 is complete. Ready for Phase 5: "Week Ahead" Frontend - Calendar View.

