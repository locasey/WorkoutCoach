# Design Analysis - Week Ahead Feature

## Overview

The Figma design has been exported as a complete React/TypeScript implementation. This document analyzes the design and identifies integration requirements.

## Design Components

### 1. WeekAheadView Component
**Location**: `design/src/components/WeekAheadView.tsx`

**Features**:
- Week/month view toggle
- Progress counter (completed/total workouts)
- Week navigation (previous/next buttons)
- 7-day grid layout for week view
- Integrates MonthView component

**State Management**:
- `viewMode`: 'week' | 'month'
- `workouts`: Array of workout objects

### 2. WorkoutCard Component
**Location**: `design/src/components/WorkoutCard.tsx`

**Features**:
- Expandable details (click to expand/collapse)
- Status indicators (completed ✓, rest -, pending)
- Displays: type, distance, duration, pace, heart rate zone, intensity, notes
- Completion toggle button
- Edit button
- Color-coded borders based on status

**Props**:
- `workout`: Workout object
- `onToggle`: Completion toggle handler
- `onEdit`: Edit handler

### 3. MonthView Component
**Location**: `design/src/components/MonthView.tsx`

**Features**:
- Full calendar month grid
- Shows workouts on specific dates
- Status indicators on calendar days
- Click to toggle completion
- Click to edit

## Design Interface vs Database Schema

### Current Database Fields
- `id`, `workout_plan_id`, `week`, `day`
- `type`, `distance_km`, `duration_minutes`, `pace`, `notes`
- `scheduled_date`, `is_completed`, `completed_at`
- `created_at`, `updated_at`

### Design Interface Fields
```typescript
interface Workout {
  id: string;
  day: string;              // "Mon", "Tue", etc. (derived from scheduled_date)
  type: string;             // ✅ Matches DB
  distance: string;         // ✅ Matches DB (format: "5km")
  status: 'completed' | 'rest' | 'pending';  // ⚠️ Needs mapping
  duration?: string;        // ✅ Matches DB (format: "30 min")
  pace?: string;            // ✅ Matches DB
  intensity?: 'low' | 'moderate' | 'high';  // ❌ Not in DB
  heartRateZone?: string;   // ❌ Not in DB
  notes?: string;           // ✅ Matches DB
}
```

## Mapping Requirements

### 1. Status Mapping
**Design**: `'completed' | 'rest' | 'pending'`  
**Database**: `is_completed: boolean` + `type: 'rest'`

**Mapping Logic**:
```typescript
function getStatus(workout: Workout): 'completed' | 'rest' | 'pending' {
  if (workout.type === 'rest') return 'rest';
  if (workout.is_completed) return 'completed';
  return 'pending';
}
```

### 2. Day Name Mapping
**Design**: `day: "Mon"`  
**Database**: `scheduled_date: Date`

**Mapping Logic**:
```typescript
function getDayName(date: Date): string {
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  return days[date.getDay()];
}
```

### 3. Distance Format
**Design**: `distance: "5km"`  
**Database**: `distance_km: 5.0`

**Mapping Logic**:
```typescript
function formatDistance(km: number | null): string {
  return km ? `${km}km` : '';
}
```

### 4. Duration Format
**Design**: `duration: "30 min"`  
**Database**: `duration_minutes: 30`

**Mapping Logic**:
```typescript
function formatDuration(minutes: number | null): string {
  return minutes ? `${minutes} min` : '';
}
```

### 5. Missing Fields: Intensity & Heart Rate Zone

**Options**:

**Option A: Add to Database** (Recommended for future)
- Add `intensity` column (ENUM: 'low', 'moderate', 'high')
- Add `heart_rate_zone` column (String)
- Requires database migration
- Allows per-workout customization

**Option B: Derive from Workout Type** (MVP approach)
```typescript
function getIntensity(type: string): 'low' | 'moderate' | 'high' {
  const intensityMap = {
    'rest': 'low',
    'easy_run': 'low',
    'long_run': 'moderate',
    'tempo': 'high',
    'intervals': 'high',
    'cross_training': 'moderate'
  };
  return intensityMap[type] || 'moderate';
}

function getHeartRateZone(type: string): string {
  const zoneMap = {
    'rest': 'Zone 1',
    'easy_run': 'Zone 2',
    'long_run': 'Zone 3',
    'tempo': 'Zone 4',
    'intervals': 'Zone 5',
    'cross_training': 'Zone 3'
  };
  return zoneMap[type] || 'Zone 2';
}
```

**Option C: Make Optional** (Simplest for MVP)
- Don't display intensity/heart rate zone if not available
- Design already handles optional fields gracefully

**Recommendation**: Use **Option B** for MVP, plan **Option A** for future enhancement.

## Integration Tasks

### Phase 5a: Component Integration
1. Copy design components to `frontend/src/components/week-ahead/`
2. Install required dependencies (Radix UI, Tailwind, Lucide icons)
3. Adapt TypeScript to JavaScript if needed (or add TypeScript to frontend)
4. Update import paths and styling

### Phase 5b: API Integration
1. Create API service functions:
   - `fetchWeekWorkouts(weekOffset)` → `GET /api/workouts/week/{offset}`
   - `toggleWorkoutCompletion(id)` → `PUT /api/workouts/{id}/complete`
   - `updateWorkout(id, data)` → `PUT /api/workouts/{id}`
   - `fetchWeekProgress(weekOffset)` → `GET /api/workouts/progress`
2. Map API responses to design interface
3. Handle loading and error states

### Phase 5c: State Management
1. Replace mock data with API calls
2. Implement week offset state management
3. Handle active plan selection
4. Update progress counter from API

### Phase 5d: Edit Functionality
1. Create edit dialog/modal component
2. Connect to `PUT /api/workouts/{id}` endpoint
3. Handle form validation
4. Update local state after edit

## Questions for Discussion

1. **Intensity & Heart Rate Zone**: Should we add these to the database now, or derive them for MVP?
2. **TypeScript**: Should we add TypeScript to the main frontend, or convert design components to JavaScript?
3. **Component Library**: The design uses shadcn/ui - should we integrate this into the main app or use simpler components?
4. **Styling**: Design uses Tailwind CSS - should we standardize on Tailwind for the entire frontend?

## Next Steps

1. ✅ Design review complete
2. ⏳ Decide on intensity/heart rate zone approach
3. ⏳ Plan component integration strategy
4. ⏳ Begin Phase 5 implementation

