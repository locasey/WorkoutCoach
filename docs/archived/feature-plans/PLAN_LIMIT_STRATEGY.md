# Workout Plan Limit Strategy

## Overview
Limit database to **5 workout plans maximum** to prevent database bloat and keep the app focused.

## Implementation Options

### Option A: User Must Delete First (Recommended for MVP)
**Behavior**: When user tries to create a 6th plan, return an error with list of existing plans.

**Pros**:
- User has full control
- No accidental deletions
- Clear feedback

**Cons**:
- Requires extra step (delete then create)
- Slightly more complex UX

**Implementation**:
```python
# In chat endpoint or WorkoutPlanService
MAX_PLANS = 5
current_count = db.query(WorkoutPlan).count()

if current_count >= MAX_PLANS:
    # Return error with list of plans
    existing_plans = WorkoutPlanService.get_all_workout_plans(db)
    return {
        "error": "Maximum of 5 workout plans allowed",
        "message": "Please delete an existing plan first",
        "existing_plans": [plan.to_dict() for plan in existing_plans],
        "current_count": current_count,
        "max_allowed": MAX_PLANS
    }
```

### Option B: Auto-Delete Oldest Inactive Plan
**Behavior**: If at limit and all plans are inactive, delete the oldest inactive plan automatically.

**Pros**:
- Seamless user experience
- No interruption

**Cons**:
- User might lose a plan they wanted to keep
- Less control

**Implementation**:
```python
MAX_PLANS = 5
current_count = db.query(WorkoutPlan).count()

if current_count >= MAX_PLANS:
    # Check if all plans are inactive
    inactive_plans = db.query(WorkoutPlan).filter(
        WorkoutPlan.is_active == False
    ).order_by(WorkoutPlan.created_at.asc()).all()
    
    if inactive_plans:
        # Delete oldest inactive plan
        oldest = inactive_plans[0]
        db.delete(oldest)
        db.commit()
    else:
        # All plans are active - return error
        return {"error": "Cannot delete active plan. Please deactivate one first."}
```

### Option C: Auto-Delete Oldest Plan (Regardless of Status)
**Behavior**: Always delete the oldest plan when at limit.

**Pros**:
- Simplest implementation
- Always works

**Cons**:
- Could delete active plan (bad UX)
- User has no control

**Not Recommended** - Could delete user's active plan unexpectedly.

## Selected Approach: Option A - User Must Delete First

**Decision**: User must manually delete a plan before creating a new one when at limit.

**Implementation**:
1. **Check limit before creating** new plan
2. **If at limit**: Return error with list of existing plans
3. **User deletes a plan** via DELETE endpoint or UI
4. **User can then create** new plan
5. **Protect active plan** - cannot delete active plan (must deactivate first)

**Benefits**:
- User has full control
- No accidental deletions
- Clear feedback about existing plans
- Simple to implement

## Configuration

Add to `backend/env.template`:
```env
# Maximum number of workout plans allowed in database
MAX_WORKOUT_PLANS=5
```

## API Response Examples

### At Limit - All Plans Active
```json
{
  "error": "Maximum workout plans reached",
  "message": "You have reached the limit of 5 workout plans. Please delete or deactivate an existing plan first.",
  "current_count": 5,
  "max_allowed": 5,
  "existing_plans": [
    {
      "id": "...",
      "goal": "...",
      "is_active": true
    }
  ]
}
```

### At Limit - Has Inactive Plans (Auto-Delete)
```json
{
  "plan_id": "...",
  "workout_plan": {...},
  "message": "Workout plan created successfully. Oldest inactive plan was automatically removed to maintain the 5-plan limit.",
  "deleted_plan": {
    "id": "...",
    "goal": "..."
  }
}
```

## Database Considerations

- **Cascade Delete**: When deleting a plan, all associated workouts are automatically deleted (via SQLAlchemy cascade)
- **No Orphaned Data**: Workouts are linked via foreign key with `cascade="all, delete-orphan"`

## Future Enhancements

- User-configurable limit (e.g., 3, 5, 10 plans)
- Archive old plans instead of deleting
- Export plan before deletion
- "Recently deleted" recovery (soft delete)

