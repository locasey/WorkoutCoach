# Post-Phase-5 Handoff: Bug Fixes & UX Improvements

claude --resume e98d861e-f7ea-4c80-bcf1-7d34c10d43b8

## What Was Completed

### Phase A: Workout Query Filtering (Critical Bug) - DONE
**File**: `backend/services/training_block_service.py` lines 170-194

Fixed `get_week_context()` to filter workouts by ownership:
- Training mode: `Workout.training_block_id == block.id`
- Maintenance mode: `training_block_id IS NULL AND workout_plan_id IS NULL`

Previously leaked ALL workouts by date range (legacy + abandoned block data).

### Phase B1: WeekHeader Simplification - DONE
**Files**: `WeekView/WeekHeader.jsx`, `WeekView/WeekHeader.css`

- Training: Single-line "Week 8 / 16 . Build Phase", countdown below, date range
- Maintenance: "This Week" + date inline, "Just Staying Fit" subtitle
- Removed: phase focus badge, lucide-react icons (Target, Calendar), reduced padding

### Phase B2: Mobile Day-Picker + Hero - DONE
**Files**: `WeekView/WeekView.jsx`, `WeekView/WeekView.css`

- Added `isMobile` state (768px breakpoint with resize listener)
- Mobile: Horizontal scrollable day pills + single DayCard hero below
- Desktop: Unchanged 7-column grid
- Day pills show distance/duration/Rest, today gets blue border

### Phase C: CoachMenu Component - DONE
**Files**: NEW `CoachMenu.jsx`, NEW `CoachMenu.css`, `App.jsx`

- Active block: Coach tab opens 3-option menu (Regenerate, New Block, Adjust Phases)
- No block: GoalSetup (unchanged)
- Bottom-sheet on mobile, centered modal on desktop

### Phase D: Maintenance Mode Messaging - DONE
**File**: `WeekView/WeekView.jsx`

- "No workouts scheduled" -> "Maintenance Mode"
- Copy: "You're in flexible training mode -- no rigid plan, just staying fit."

### Bonus: Added missing `.week-view__empty-cta` CSS

---

## What Remains (Interrupted by Disk Space)

### Fix 1: Add Workout Broken - NOT STARTED (code written, not saved)

**Root Cause**: `POST /api/workouts/day` endpoint (`app.py:996`) requires `workout_plan_id` and calls `WorkoutPlanService.add_workout_to_day()`. Frontend sends `weekData.block_id` as `workout_plan_id`, but that's a TrainingBlock UUID, not a WorkoutPlan UUID. The lookup fails.

**Fix needed in `backend/app.py` lines 1025-1039**:
- Accept `training_block_id` as alternative to `workout_plan_id`
- When `training_block_id` provided: validate block exists, check existing workouts for day limit (max 2), handle slot assignment, create Workout with `training_block_id` field
- Keep legacy `workout_plan_id` path for backward compatibility

**Fix needed in `frontend/src/components/WeekView/WeekView.jsx` addWorkoutMutation**:
- Change `workout_plan_id: weekData?.block_id` to `training_block_id: weekData?.block_id`

### Fix 2: Start Date Selection in GoalSetup - NOT STARTED

**File**: `frontend/src/components/GoalSetup/RaceDetails.jsx`

Currently auto-calculates `start_date` from `target_date - total_weeks` (backend default). User should choose:
1. **Today** (default) - start immediately
2. **Next Monday** - calculated from current date
3. **Custom date** - date picker

Changes needed:
- Add `startDate` state and 3 radio options below the Race Date field
- Pass `start_date` in the `handleGenerate` call in `GoalSetup.jsx` line 113
- Backend already accepts `start_date` (app.py line 531-533, TrainingBlockService line 74-75)

### Fix 3: WeekNav "Return to Current Week" - NOT STARTED

**File**: `frontend/src/components/WeekView/WeekNav.jsx`

Make `week-nav__current` div clickable when `weekOffset !== 0`:
- Wrap in `<button>` (or add onClick) that calls `onWeekChange(0)`
- Add CSS: `cursor: pointer` when not current, hover tooltip "Return to Current Week"
- CSS in `WeekNav.css`: add `.week-nav__current:not(.week-nav__current--active)` hover styles

### Fix 4: Color-Code WeekHeader Phase - NOT STARTED

**File**: `frontend/src/components/WeekView/WeekHeader.css`

Add phase-specific colors to `.week-header__phase` matching existing `.phase-badge[data-phase]`:
```css
.week-header__phase[data-phase="base"]  { color: #5a8a6a; }
.week-header__phase[data-phase="build"] { color: var(--persian-blue); }
.week-header__phase[data-phase="peak"]  { color: var(--rust-brown); }
.week-header__phase[data-phase="taper"] { color: var(--success-green); }
```

Also update `WeekHeader.jsx` to add `data-phase={phase}` attribute to the span.

### Fix 5: Header Tagline Update - NOT STARTED

**File**: `frontend/src/App.jsx` line 156

Change:
```jsx
<p>Your AI-powered training companion</p>
```
To:
```jsx
<p>Plan your work(out), work your plan</p>
```

---

## File Summary

| File | Status | Changes |
|------|--------|---------|
| `backend/services/training_block_service.py` | SAVED | Query filtering fix |
| `frontend/src/components/WeekView/WeekHeader.jsx` | SAVED | Simplified, icons removed |
| `frontend/src/components/WeekView/WeekHeader.css` | SAVED | Compact styles |
| `frontend/src/components/WeekView/WeekView.jsx` | SAVED | Mobile day-picker, maintenance msg |
| `frontend/src/components/WeekView/WeekView.css` | SAVED | Day-picker styles, CTA button |
| `frontend/src/components/CoachMenu.jsx` | SAVED | New component |
| `frontend/src/components/CoachMenu.css` | SAVED | New styles |
| `frontend/src/App.jsx` | SAVED | CoachMenu integration |
| `backend/app.py` | NEEDS EDIT | Add workout fix (Fix 1) |
| `frontend/src/components/GoalSetup/RaceDetails.jsx` | NEEDS EDIT | Start date (Fix 2) |
| `frontend/src/components/WeekView/WeekNav.jsx` | NEEDS EDIT | Return to current (Fix 3) |
| `frontend/src/components/WeekView/WeekHeader.jsx` | NEEDS EDIT | Phase colors (Fix 4) |
| `frontend/src/App.jsx` | NEEDS EDIT | Tagline (Fix 5) |
