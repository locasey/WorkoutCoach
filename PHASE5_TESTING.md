# Phase 5 Testing Guide - Week Ahead Feature

## Prerequisites

1. **Backend Server**: Running on `http://localhost:5000`
2. **Frontend Server**: Running on `http://localhost:3000` (or port shown in terminal)
3. **Database**: Neon database connected and migrations run
4. **Active Workout Plan**: At least one workout plan should be created and set as active

## Test Scenarios

### 1. Basic Week View Display
- [ ] Navigate to "Your Week Ahead" tab
- [ ] Verify week calendar grid displays (Mon-Sun columns)
- [ ] Check that workouts from active plan are displayed
- [ ] Verify workout cards show:
  - Day name (Mon, Tue, etc.)
  - Workout type (e.g., "Easy Run", "Tempo Run")
  - Distance (e.g., "5km")
  - Completion checkbox
  - Edit button

### 2. Workout Card Expansion
- [ ] Click on a workout card to expand
- [ ] Verify expanded details show:
  - Duration (if available)
  - Pace (if available)
  - Heart rate zone
  - Intensity bar (low/moderate/high)
  - Notes (if available)
- [ ] Click again to collapse

### 3. Completion Toggle
- [ ] Click completion checkbox on a pending workout
- [ ] Verify checkbox changes to checked (green)
- [ ] Verify progress counter updates (e.g., "2/5 workouts completed")
- [ ] Click again to uncheck
- [ ] Verify workout returns to pending state
- [ ] Verify progress counter decreases

### 4. Week Navigation
- [ ] Click "Previous Week" button (←)
- [ ] Verify workouts for previous week load
- [ ] Verify week range in header updates
- [ ] Click "Next Week" button (→)
- [ ] Verify workouts for next week load
- [ ] Navigate back to current week (week offset 0)

### 5. Month View
- [ ] Click "Month View" button
- [ ] Verify monthly calendar grid displays
- [ ] Verify workouts are shown on correct dates
- [ ] Check that workout indicators appear on days with workouts
- [ ] Verify completion status is shown (green dot for completed, blue for pending, brown for rest)

### 6. Month Navigation
- [ ] In month view, click "Previous Month" button (←)
- [ ] Verify previous month's workouts load
- [ ] Click "Next Month" button (→)
- [ ] Verify next month's workouts load
- [ ] Navigate back to current month

### 7. Week/Month Toggle
- [ ] From week view, switch to month view
- [ ] Verify smooth transition
- [ ] From month view, switch back to week view
- [ ] Verify returns to current week

### 8. Empty States
- [ ] Navigate to a week with no workouts
- [ ] Verify "No workout scheduled" message appears for empty days
- [ ] Verify no errors in console

### 9. Loading States
- [ ] Refresh page while on Week Ahead tab
- [ ] Verify "Loading workouts..." message appears briefly
- [ ] Verify workouts load without errors

### 10. Error Handling
- [ ] Stop backend server temporarily
- [ ] Try to navigate weeks
- [ ] Verify error message displays (should show "Failed to load workouts")
- [ ] Restart backend server
- [ ] Verify workouts load again

### 11. Progress Counter
- [ ] Complete multiple workouts
- [ ] Verify progress counter updates: "X/Y workouts completed"
- [ ] Verify counter only counts non-rest workouts
- [ ] Verify counter updates in real-time when toggling completion

### 12. Rest Day Handling
- [ ] Find a rest day workout
- [ ] Verify it shows "Rest" type
- [ ] Verify completion checkbox is disabled (brown/gray)
- [ ] Verify edit button still works

### 13. Edit Functionality (Placeholder)
- [ ] Click edit button on any workout
- [ ] Verify alert appears: "Edit functionality coming in Phase 7!"
- [ ] This is expected - full edit UI will be in Phase 7

### 14. Responsive Design
- [ ] Resize browser window to mobile size
- [ ] Verify week grid adapts (may scroll horizontally)
- [ ] Verify workout cards remain readable
- [ ] Verify buttons are still clickable

### 15. Data Persistence
- [ ] Complete a workout
- [ ] Navigate to different week
- [ ] Navigate back
- [ ] Verify workout remains completed
- [ ] Refresh page
- [ ] Verify completed status persists

## Expected Behavior

### Color Coding
- **Completed workouts**: Green border and background (`#8eb19d`)
- **Pending workouts**: Blue border (`#072ac8`)
- **Rest days**: Brown/orange border (`#a44200`)
- **Background**: Almond silk (`#eacdc2`)

### Workout Types
- Should display as "Title Case" (e.g., "Easy Run", "Tempo Run", "Long Run")
- Rest days should show as "Rest"

### Intensity Levels
- **Low**: Easy runs, recovery runs → 33% bar, green
- **Moderate**: Long runs → 66% bar, blue
- **High**: Tempo runs, intervals → 100% bar, brown

### Heart Rate Zones
- **Zone 2**: Easy runs
- **Zone 3**: Long runs
- **Zone 4**: Tempo runs, intervals
- **Rest**: Rest days

## Troubleshooting

### No workouts showing
1. Check if you have an active workout plan
2. Verify backend is running and connected to database
3. Check browser console for errors
4. Verify API calls in Network tab

### Completion toggle not working
1. Check browser console for API errors
2. Verify workout ID is valid (not a placeholder)
3. Check backend logs for errors

### Month view not loading
1. Verify backend endpoint `/api/workouts/month/{year}/{month}` is working
2. Check that workouts have `scheduled_date` set
3. Verify month/year parameters are valid (1-12 for month)

### Styling issues
1. Verify Tailwind CSS is compiled (check if classes are applied)
2. Clear browser cache
3. Restart frontend dev server

## Test Data Setup

If you need test data:
1. Use the chat interface to generate a workout plan
2. Set the plan as active (via API or future UI)
3. Verify workouts are created with scheduled dates

## Success Criteria

✅ All test scenarios pass
✅ No console errors
✅ UI matches design mockup
✅ API calls succeed
✅ Data persists correctly
✅ Navigation works smoothly
✅ Responsive design functions

