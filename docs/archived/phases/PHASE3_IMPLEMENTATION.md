# Phase 3 Implementation: Week View Backend API

## Overview

Phase 3 implements the backend API endpoints needed to support the "Week Ahead" calendar view feature. This includes endpoints for fetching workouts by week/month, toggling completion status, and getting progress summaries.

## API Endpoints

### 1. Get Current Week Workouts
**Endpoint**: `GET /api/workouts/week`

**Description**: Returns all workouts for the current calendar week (Monday-Sunday).

**Response**:
```json
{
  "week_start": "2026-01-05",
  "week_end": "2026-01-11",
  "workouts": [
    {
      "id": "...",
      "type": "easy_run",
      "scheduled_date": "2026-01-10",
      "is_completed": false,
      ...
    }
  ],
  "count": 2
}
```

### 2. Get Week by Offset
**Endpoint**: `GET /api/workouts/week/<week_offset>`

**Description**: Returns workouts for a specific week relative to current week.
- `0` = current week
- `-1` = last week
- `+1` = next week
- etc.

**Response**: Same format as current week endpoint, with additional `week_offset` field.

### 3. Get Month Workouts
**Endpoint**: `GET /api/workouts/month/<year>/<month>`

**Description**: Returns all workouts for a specific calendar month.

**Parameters**:
- `year`: Year (e.g., 2026)
- `month`: Month (1-12)

**Response**:
```json
{
  "year": 2026,
  "month": 1,
  "workouts": [...],
  "count": 22
}
```

**Error Handling**: Returns 400 if month is not between 1-12.

### 4. Toggle Workout Completion
**Endpoint**: `PUT /api/workouts/<workout_id>/complete`

**Description**: Toggles the completion status of a workout.

**Response**:
```json
{
  "workout": {
    "id": "...",
    "is_completed": true,
    "completed_at": "2026-01-10T12:00:00",
    ...
  },
  "message": "Workout marked as completed"
}
```

**Error Handling**: Returns 404 if workout not found, 400 if invalid workout ID format.

### 5. Get Week Progress
**Endpoint**: `GET /api/workouts/progress?week_offset=0`

**Description**: Returns progress summary for a week.

**Query Parameters**:
- `week_offset` (optional): Week offset (default: 0 for current week)

**Response**:
```json
{
  "week_start": "2026-01-05",
  "week_end": "2026-01-11",
  "total_workouts": 7,
  "completed_workouts": 3,
  "incomplete_workouts": 4,
  "completion_percentage": 42.9,
  "workouts_by_day": {
    "2026-01-05": [...],
    "2026-01-06": [...]
  }
}
```

## Service Layer Changes

### New Helper Functions (`WorkoutPlanService`)

1. **`get_week_start_end(target_date=None)`**
   - Returns (Monday, Sunday) dates for a calendar week
   - Defaults to current week if no date provided

2. **`get_week_by_offset(week_offset=0)`**
   - Returns week dates by offset from current week
   - Supports positive (future) and negative (past) offsets

3. **`get_month_start_end(year, month)`**
   - Returns first and last day of a calendar month

### New Service Methods

1. **`get_workouts_for_month(db, year, month, user_id=None)`**
   - Fetches all workouts for a calendar month from active plan

2. **`get_week_progress(db, week_start, week_end, user_id=None)`**
   - Calculates progress statistics for a week
   - Returns completion percentage and workouts grouped by day

## Behavior Notes

- **Active Plan Only**: All endpoints only return workouts from the currently active workout plan
- **No Active Plan**: If no active plan exists, endpoints return empty results (not errors)
- **Date Calculations**: Calendar weeks start on Monday and end on Sunday
- **Completion Tracking**: `completed_at` timestamp is automatically set/unset when toggling

## Testing

Test script: `backend/scripts/test_phase3.py`

**Test Coverage**:
- ✅ Current week workouts retrieval
- ✅ Week offset queries (current, next, last)
- ✅ Month workouts retrieval
- ✅ Workout completion toggling
- ✅ Progress summary calculation
- ✅ Progress with week offset parameter
- ✅ Edge cases (invalid month, invalid workout ID, no active plan)

**Run Tests**:
```bash
cd backend
python scripts/test_phase3.py
```

## Next Steps

Phase 3 is complete. Ready for Phase 4: Workout Editing API.

