# LOC-20 + LOC-22: Rest Day Editing & Multiple Workouts Per Day

> **Status:** ✅ Implementation Complete (100%)
> **Last Updated:** 2026-02-04

## Summary

**LOC-20 (Bug):** Rest days cannot be edited on mobile. Fix by showing Edit button and removing Mark Complete button for rest days.

**LOC-22 (Feature):** Support up to 2 workouts per day with AM/PM visual positioning. Rest can occupy any slot.

---

## Phase 1: Database Schema Change ✅

**File:** `backend/models/workout.py`

Add `slot` column after `day`:
```python
day = Column(Integer, nullable=False)  # 1-7, where 1=Monday
slot = Column(Integer, nullable=True)  # NULL=single, 1=AM/first, 2=PM/second
```

**File:** `backend/alembic/versions/xxxx_add_workout_slot.py`

Create migration:
```python
# UP
def upgrade():
    op.add_column('workouts', sa.Column('slot', sa.Integer(), nullable=True))

# DOWN
def downgrade():
    op.drop_column('workouts', 'slot')
```

**Update `to_dict()`** in workout.py:
```python
'slot': self.slot,
```

---

## Phase 2: Backend Service Updates ✅

**File:** `backend/services/workout_plan_service.py`

### 2.1 Update week/month queries to group by day

Current queries return flat list. Update to support multiple per day:
```python
# No change to return format - frontend will group by date
# But add slot to ordering
.order_by(Workout.scheduled_date, Workout.slot.nullsfirst())
```

### 2.2 Add validation for max 2 workouts per day

```python
@staticmethod
def validate_workout_slot(db, workout_plan_id, scheduled_date, slot, exclude_workout_id=None):
    """Validate slot is available (max 2 per day)."""
    query = db.query(Workout).filter(
        Workout.workout_plan_id == workout_plan_id,
        Workout.scheduled_date == scheduled_date
    )
    if exclude_workout_id:
        query = query.filter(Workout.id != exclude_workout_id)

    existing = query.all()

    if len(existing) >= 2:
        raise ValueError("Maximum 2 workouts per day")

    if slot and any(w.slot == slot for w in existing):
        raise ValueError(f"Slot {slot} already occupied for this day")

    return True
```

### 2.3 Add method to create additional workout for a day

```python
@staticmethod
def add_workout_to_day(db, workout_plan_id, scheduled_date, workout_data):
    """Add a second workout to an existing day."""
    # Get existing workouts for this day
    existing = db.query(Workout).filter(
        Workout.workout_plan_id == workout_plan_id,
        Workout.scheduled_date == scheduled_date
    ).all()

    if len(existing) >= 2:
        raise ValueError("Maximum 2 workouts per day")

    if len(existing) == 1:
        # Upgrade existing workout to slot 1 (AM) if it has no slot
        if existing[0].slot is None:
            existing[0].slot = 1
        # New workout gets slot 2 (PM)
        workout_data['slot'] = 2

    # Create the new workout
    # ... (similar to existing create logic)
```

---

## Phase 3: Backend API Updates ✅

**File:** `backend/app.py`

### 3.1 New endpoint to add workout to day

```python
@app.route('/api/workouts/day', methods=['POST'])
def add_workout_to_day():
    """Add an additional workout to a specific day."""
    data = request.get_json()

    required = ['workout_plan_id', 'scheduled_date']
    # ... validation

    db = next(get_db())
    try:
        workout = WorkoutPlanService.add_workout_to_day(
            db,
            uuid.UUID(data['workout_plan_id']),
            data['scheduled_date'],
            data
        )
        return jsonify({'workout': workout.to_dict()}), 201
    finally:
        db.close()
```

### 3.2 Update workout update endpoint

Ensure slot changes are validated:
```python
@app.route('/api/workouts/<workout_id>', methods=['PUT'])
def update_workout(workout_id):
    # ... existing code
    # Add slot validation if slot is being changed
```

---

## Phase 4: Frontend - Workout Mapper ✅

**File:** `frontend/src/utils/workoutMapper.js`

Update `mapWorkoutToDesign()`:
```javascript
return {
  // ... existing fields
  slot: dbWorkout.slot || null,  // null=single, 1=AM, 2=PM
  scheduledDate: dbWorkout.scheduled_date || null,
  // ...
};
```

---

## Phase 5: Frontend - WeekAheadView (LOC-20 + LOC-22) ✅

**File:** `frontend/src/components/WeekAheadView.jsx`

### 5.1 LOC-20: Fix mobile hero for rest days (lines 506-571)

**Current structure:**
```jsx
{activeWorkout.status !== 'rest' && activeWorkout.type && (
  <> {/* metrics + Edit + Mark Complete */} </>
)}
{activeWorkout.status === 'rest' && (
  <p>Enjoy your rest day!</p>
)}
```

**New structure:**
```jsx
{activeWorkout.type && (
  <>
    {activeWorkout.status !== 'rest' && (
      <div className="hero-metrics">...</div>
    )}

    {activeWorkout.notes && activeWorkout.status !== 'rest' && (
      <p className="hero-description">...</p>
    )}

    {activeWorkout.status === 'rest' && (
      <p className="hero-description mt-4">
        Enjoy your rest day! Recovery is just as important as the work.
      </p>
    )}

    <div className="hero-actions">
      {/* Mark Complete - ONLY for non-rest */}
      {activeWorkout.status !== 'rest' && (
        <button onClick={() => toggleWorkoutStatus(activeWorkout.id)} className="btn-hero btn-hero-primary">
          <CheckCircle className="w-5 h-5" />
          {activeWorkout.status === 'completed' ? 'Unmark Complete' : 'Mark Complete'}
        </button>
      )}

      {/* Edit - ALWAYS shown */}
      <button onClick={() => handleEdit(activeWorkout.id)} className="btn-hero btn-hero-secondary">
        <Edit3 className="w-5 h-5" />
        Edit
      </button>
    </div>
  </>
)}
```

### 5.2 LOC-22: Group workouts by day

Update data processing to group workouts:
```javascript
// In fetchWeekWorkouts, after mapping:
const groupedByDay = {};
mappedWorkouts.forEach(workout => {
  const key = workout.scheduledDate || workout.day;
  if (!groupedByDay[key]) {
    groupedByDay[key] = [];
  }
  groupedByDay[key].push(workout);
  // Sort by slot (null first, then 1, then 2)
  groupedByDay[key].sort((a, b) => (a.slot || 0) - (b.slot || 0));
});
```

### 5.3 LOC-22: Mobile hero for multiple workouts

When a day has 2 workouts, show both in hero section:
```jsx
{dayWorkouts.length === 1 ? (
  <SingleWorkoutHero workout={dayWorkouts[0]} />
) : (
  <MultiWorkoutHero workouts={dayWorkouts} /> // AM on top, PM on bottom
)}
```

### 5.4 LOC-22: Add workout button

Show "+" button when day has < 2 workouts:
```jsx
{dayWorkouts.length < 2 && (
  <button
    onClick={() => handleAddWorkout(activeDay.scheduledDate)}
    className="btn-hero btn-hero-secondary"
  >
    <Plus className="w-5 h-5" />
    Add Workout
  </button>
)}
```

---

## Phase 6: Frontend - WorkoutCard (LOC-20 + LOC-22) ✅

**File:** `frontend/src/components/WorkoutCard.jsx`

### 6.1 LOC-20: Remove Mark Complete for rest days

**Current (line 73-81):**
```jsx
<button
  onClick={onToggle}
  disabled={workout.status === 'rest'}
  ...
>
```

**New:**
```jsx
{workout.status !== 'rest' && (
  <button onClick={onToggle} ...>
    <Check className="w-5 h-5" />
  </button>
)}
```

### 6.2 LOC-22: Handle card receiving array of workouts

Option A: WorkoutCard receives single workout, parent stacks them
Option B: WorkoutCard can render 1-2 workouts

**Recommend Option A** - simpler, parent handles grouping:
```jsx
// In WeekAheadView desktop grid:
{Object.entries(groupedWorkouts).map(([day, dayWorkouts]) => (
  <div key={day} className="workout-day-column">
    {dayWorkouts.map((workout, idx) => (
      <WorkoutCard
        key={workout.id}
        workout={workout}
        isAM={dayWorkouts.length > 1 && idx === 0}
        isPM={dayWorkouts.length > 1 && idx === 1}
        ...
      />
    ))}
    {dayWorkouts.length < 2 && (
      <AddWorkoutButton date={dayWorkouts[0]?.scheduledDate} />
    )}
  </div>
))}
```

### 6.3 LOC-22: Visual AM/PM indicator

Add subtle visual indicator for slot when 2 workouts:
```jsx
{(isAM || isPM) && (
  <div className="slot-indicator">
    {isAM ? 'AM' : 'PM'}
  </div>
)}
```

---

## Phase 7: Frontend - MonthView (LOC-22) ✅

**File:** `frontend/src/components/MonthView.jsx`

Update to show multiple workouts per day cell:
```jsx
{day.workouts?.map((workout, idx) => (
  <div key={workout.id} className={`workout-entry ${idx > 0 ? 'mt-1' : ''}`}>
    <span className="text-xs">{workout.type}</span>
    {day.workouts.length > 1 && (
      <span className="slot-badge">{idx === 0 ? 'AM' : 'PM'}</span>
    )}
  </div>
))}
```

---

## Phase 8: Frontend - WorkoutEditModal ✅

**File:** `frontend/src/components/WorkoutEditModal.jsx`

When adding a new workout to a day that already has one, the modal should:
1. Pre-set slot to 2 (PM) since existing gets slot 1 (AM)
2. No slot selector needed - backend handles it

No major changes needed - the "Add Workout" flow will call a new function that passes the date, and backend assigns slots automatically.

---

## Testing Checklist

### LOC-20 (Rest Day Editing)
- [ ] Mobile: Edit button visible for rest days
- [ ] Mobile: "Enjoy your rest day!" message shown
- [ ] Mobile: Mark Complete button NOT shown for rest days
- [ ] Desktop WorkoutCard: Edit button visible for rest days
- [ ] Desktop WorkoutCard: Mark Complete button NOT shown for rest days
- [ ] MonthView: Edit button visible for rest days
- [ ] MonthView: Mark Complete button NOT shown for rest days
- [ ] Can change rest day to workout type via Edit modal
- [ ] Can change workout to rest type via Edit modal

### LOC-22 (Multiple Workouts Per Day)
- [ ] Can add second workout to a day via "+" button
- [ ] Cannot add third workout (validation error)
- [ ] Single workout shows no AM/PM indicator
- [ ] Two workouts show AM (top) / PM (bottom) positioning
- [ ] Rest can be added as PM slot
- [ ] Week view displays stacked workouts correctly
- [ ] Month view displays multiple workouts per day
- [ ] Mobile hero handles 2 workouts
- [ ] Day picker shows primary workout info (first slot)
- [ ] Editing either workout works correctly
- [ ] Completing either workout works correctly
- [ ] Deleting one workout demotes remaining to no-slot

---

## Files Changed

| File | LOC-20 | LOC-22 |
|------|--------|--------|
| `backend/models/workout.py` | | X |
| `backend/alembic/versions/xxxx_add_slot.py` | | X |
| `backend/services/workout_plan_service.py` | | X |
| `backend/app.py` | | X |
| `frontend/src/utils/workoutMapper.js` | | X |
| `frontend/src/components/WeekAheadView.jsx` | X | X |
| `frontend/src/components/WorkoutCard.jsx` | X | X |
| `frontend/src/components/MonthView.jsx` | | X |
| `frontend/src/components/WorkoutEditModal.jsx` | | X (minor) |

---

## Risks

- **Medium**: Database migration required - test on staging first
- **Low**: LOC-20 changes isolated to conditional rendering
- **Medium**: LOC-22 changes touch multiple views - thorough testing needed

## Migration Strategy

1. Deploy backend with migration first (slot column is nullable, backward compatible)
2. Deploy frontend changes
3. Existing workouts keep `slot=NULL` (displayed as single/blank)
