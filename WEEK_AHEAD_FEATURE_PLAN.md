# "Your Week Ahead" Feature - Development Plan

## 🎯 Feature Overview

A visual dashboard that shows users their upcoming workouts for the week, tracks progress against planned workouts, and automatically syncs with Strava activities to show completion status.

## ✅ Requirements (Confirmed)

### Database & Data Model
- **Database**: PostgreSQL (with Google Cloud SQL for future hosting)
- **Progress Tracking**: Simple Completed/Not Completed (for MVP)
- **Historical Data**: Keep all workout plans, track which is "active"
- **User Management**: Single user for MVP (design extensible for multi-user later)

### "Week Ahead" View Design
- **Time Range**: Current calendar week (Monday-Sunday)
- **Visualization Style**: Weekly calendar grid view
- **Navigation**: Easy click to expand to monthly calendar view
- **Key Metrics**: 
  - Total workouts planned for week
  - Completed vs. planned count
  - Visual progress indicators
- **Workout Details**: 
  - Workout type, distance, pace, notes
  - Completion status (checkbox/toggle)
  - Editable inline

### Strava Integration (Post-MVP)
- **Matching Logic**: 
  - MVP: Date only (any activity on that day counts)
  - Advanced: Date + distance range matching
  - Manual confirmation option
- **Auto-sync**: Manual "Sync Now" button (future feature)

### MVP Scope
**Must-Have Features**:
- [x] Create workout plan (via chat or import)
- [x] Select workout plan as "active"
- [x] View current week's workouts in calendar grid
- [x] Mark workouts as completed/not completed
- [x] Edit workouts manually (inline editing)
- [x] Navigate to monthly calendar view
- [x] Visual progress indicators

**Post-MVP Features**:
- [ ] Strava auto-sync and matching
- [ ] Historical weeks view
- [ ] Detailed metrics/comparisons
- [ ] Notifications/reminders

## 🗄️ Database Schema

### Database Choice
- **PostgreSQL** for production-ready setup
- **Google Cloud SQL** compatible (for future hosting on GCP free tier)
- Using **SQLAlchemy** ORM for Python integration

### Tables Needed

#### `workout_plans`
- `id` (primary key, UUID or serial)
- `user_id` (integer, nullable for MVP - single user)
- `goal` (text) - e.g., "12-week half marathon"
- `duration_weeks` (integer)
- `start_date` (date) - when the plan starts (for date calculations)
- `created_at` (timestamp)
- `is_active` (boolean, default false) - only one active plan at a time
- `user_request` (text) - original chat request
- `plan_data` (JSONB, optional) - full plan JSON for reference

#### `workouts`
- `id` (primary key, UUID or serial)
- `workout_plan_id` (foreign key to workout_plans)
- `week` (integer, 1-based)
- `day` (integer, 1-7, where 1=Monday)
- `type` (text: long_run, tempo, intervals, easy_run, rest, cross_training)
- `distance_km` (float, nullable)
- `duration_minutes` (integer, nullable)
- `pace` (text, nullable)
- `notes` (text, nullable)
- `scheduled_date` (date) - calculated from plan start_date + week/day
- `is_completed` (boolean, default false) - simple completion status
- `completed_at` (timestamp, nullable)
- `created_at` (timestamp)
- `updated_at` (timestamp)

#### `workout_completions` (Future - for Strava integration)
- `id` (primary key)
- `workout_id` (foreign key)
- `strava_activity_id` (text, nullable)
- `completed_date` (timestamp)
- `actual_distance_km` (float, nullable)
- `actual_duration_minutes` (integer, nullable)
- `actual_pace` (text, nullable)
- `matching_method` (text: date_only, date_distance, manual)
- `notes` (text, nullable)

#### `strava_activities` (Future - for caching)
- `id` (primary key)
- `strava_id` (text, unique)
- `activity_type` (text)
- `activity_date` (timestamp)
- `distance_km` (float)
- `duration_minutes` (integer)
- `pace` (text)
- `synced_at` (timestamp)

## 🚀 Development Phases

### Phase 1: Database Foundation & Setup ✅ COMPLETED
**Goal**: Set up PostgreSQL database and migrate from in-memory storage

**Tasks**:
- [x] Set up PostgreSQL locally (or use Docker) - Docker Compose file created
- [x] Install SQLAlchemy and PostgreSQL driver (psycopg2) - Added to requirements.txt
- [x] Design and create database schema (workout_plans, workouts tables) - Models created
- [x] Create SQLAlchemy models - WorkoutPlan and Workout models implemented
- [x] Set up database migrations (Alembic) - Alembic configured
- [x] Create database connection and session management - database.py created
- [x] Update workout plan generation to save to database - Chat endpoint updated
- [x] Create seed/test data - Seed script created
- [x] Test data persistence and retrieval - Service layer implemented

**Deliverable**: PostgreSQL database running, workout plans saved to DB ✅
 
**Implementation Notes**:
- Created `backend/models/` with WorkoutPlan and Workout models
- Created `backend/database.py` for connection management
- Created `backend/services/workout_plan_service.py` for business logic
- Updated `backend/app.py` to save plans to database
- Added Docker Compose for easy PostgreSQL setup
- Created database initialization and seeding scripts
- Added DATABASE_SETUP.md guide

**Tech Stack**:
- PostgreSQL (local for dev, Cloud SQL for production)
- SQLAlchemy ORM
- Alembic for migrations
- psycopg2-binary for PostgreSQL driver

---

### Phase 1b: Neon Cloud Database Migration (IMMEDIATE) ✅ COMPLETED
**Goal**: Migrate from local Docker PostgreSQL to Neon cloud database to reduce local resource usage

**Tasks**:
- [x] Create Neon account and project (https://neon.tech)
- [x] Create new PostgreSQL database on Neon
- [x] Get Neon connection string (with credentials)
- [x] Update `.env` template with Neon database URL
- [x] Update `database.py` to use Neon connection string from environment
- [x] Test connection to Neon database
- [x] Run Alembic migrations on Neon database
- [x] Migrate existing data from local DB to Neon (if any)
- [x] Update documentation with Neon setup instructions (NEON_SETUP.md created)
- [x] Stop/remove Docker Compose PostgreSQL setup (WSL/Docker shut down)
- [x] Test all database operations with Neon
- [x] Verify app works with Neon database

**Deliverable**: Application running on Neon cloud database, Docker PostgreSQL removed ✅

**Implementation Notes**:
- Neon database successfully set up and connected
- Migrations run successfully
- Workout plans verified saving to Neon
- Docker/WSL no longer needed (reduced CPU usage)
- Database accessible from anywhere

**Benefits**:
- ✅ No local Docker resource usage
- ✅ Accessible from anywhere
- ✅ Automatic backups
- ✅ Free tier available
- ✅ Easy to access from multiple devices

**Tech Stack**:
- Neon (serverless PostgreSQL)
- Connection string format: `postgresql://user:password@host/dbname`
- Same SQLAlchemy setup (minimal code changes)
- Connection pooling recommended

---

### Phase 2: Workout Plan Management API ✅ COMPLETED
**Goal**: Build API for creating, selecting, and managing workout plans

**Tasks**:
- [x] Update `POST /api/chat` to save plan to database
- [x] **Implement plan limit (5 plans max)** - Prevent database bloat
  - [x] Check plan count before creating new plan
  - [x] If at limit: return error with list of existing plans
  - [x] Add logic to handle limit (Option A: user must delete first)
- [x] Create endpoint: `GET /api/workout-plans` - List all plans
- [x] Create endpoint: `GET /api/workout-plans/{id}` - Get specific plan
- [x] Create endpoint: `POST /api/workout-plans/{id}/activate` - Set plan as active
- [x] Create endpoint: `DELETE /api/workout-plans/{id}` - Delete a plan
- [x] Create endpoint: `GET /api/workout-plans/active` - Get current active plan
- [x] Add validation (only one active plan at a time)
- [x] Add plan start_date calculation/assignment
- [x] Update Excel export to use database

**Deliverable**: Can create plans (up to 5), set one as active, and delete old plans ✅

**Implementation Notes**:
- Added `check_plan_limit()` and `delete_workout_plan()` to WorkoutPlanService
- All endpoints now use database instead of in-memory storage
- Plan limit enforced with clear error messages
- Active plan protection (cannot delete active plan)
- See PHASE2_IMPLEMENTATION.md for API documentation

**Testing**:
- ✅ Test script created: `backend/scripts/test_phase2.py`
- ✅ All endpoints tested and working
- ✅ Plan limit enforcement verified
- ✅ Active plan protection verified
- ✅ Error handling verified

**Plan Limit Management Strategy** (Option A - Selected):
- **Limit**: Maximum 5 workout plans in database
- **When creating new plan at limit**: Return error with list of existing plans, user must delete one first
- **User can delete plans** via DELETE endpoint
- **Active plan is protected** - cannot delete active plan (must deactivate first)
- **User has full control** - no automatic deletions

---

### Phase 3: Week View Backend API ✅ COMPLETED
**Goal**: Build API endpoints to support the week calendar view

**Tasks**:
- [x] Create endpoint: `GET /api/workouts/week` - Get workouts for current calendar week
- [x] Create endpoint: `GET /api/workouts/week/{week_offset}` - Get specific week (0=current, -1=last, +1=next)
- [x] Create endpoint: `GET /api/workouts/month/{year}/{month}` - Get workouts for a month
- [x] Create endpoint: `PUT /api/workouts/{id}/complete` - Toggle completion status
- [x] Create endpoint: `GET /api/workouts/progress` - Get progress summary for week
- [x] Add date calculation logic (determine calendar week, scheduled dates)
- [x] Add completion status to workout responses
- [x] Handle edge cases (no active plan, plan hasn't started yet)
- [x] **Testing**: Create test script and verify all endpoints
- [x] **Testing**: Test date calculations (current week, week offsets)
- [x] **Testing**: Test edge cases (no active plan, empty weeks)

**Deliverable**: Backend API ready to serve week/month view data ✅

**Implementation Notes**:
- Added date helper functions: `get_week_start_end()`, `get_week_by_offset()`, `get_month_start_end()`
- Added service methods: `get_workouts_for_month()`, `get_week_progress()`
- All endpoints return workouts from active plan only
- Progress endpoint includes completion percentage and workouts grouped by day
- Edge cases handled: invalid month (400), invalid workout ID (404), no active plan (empty results)
- Test script: `backend/scripts/test_phase3.py` - All tests passing ✅

---

### Phase 4: Workout Editing API ✅ COMPLETED
**Goal**: Allow manual editing of workout details

**Tasks**:
- [x] Create endpoint: `PUT /api/workouts/{id}` - Update workout details
- [x] Add validation for workout fields (type, distance, pace, notes)
- [x] Handle partial updates (only update fields provided)
- [x] Add `updated_at` timestamp tracking
- [x] **Testing**: Create test script and verify editing works
- [x] **Testing**: Test validation (invalid fields, missing data)
- [x] **Testing**: Test partial updates

**Deliverable**: Workouts can be edited via API ✅

**Implementation Notes**:
- Added `update_workout()` method to WorkoutPlanService with comprehensive validation
- Validates workout type (must be from allowed list)
- Validates distance_km (must be non-negative number)
- Validates duration_minutes (must be non-negative integer)
- Validates pace and notes (must be strings if provided)
- Supports partial updates (only provided fields are updated)
- Supports clearing fields (set to None)
- `updated_at` timestamp automatically tracked by SQLAlchemy
- Test script: `backend/scripts/test_phase4.py` - All tests passing ✅

---

### Phase 5: "Week Ahead" Frontend - Calendar View
**Goal**: Build the visual weekly calendar dashboard

**Tasks**:
- [x] Design mockup/wireframe for week calendar view (Figma mockup created)
- [x] **Review Figma mockup**: Design exported to `design/` folder with full React/TypeScript implementation
- [x] Integrate design components into main frontend app
- [x] Connect WeekAheadView to backend API (`GET /api/workouts/week`)
- [x] Map database fields to design interface (status, intensity, heartRateZone)
- [x] Implement expandable workout cards (click to show details)
- [x] Implement completion toggle (connect to `PUT /api/workouts/{id}/complete`)
- [x] Implement edit functionality placeholder (connect to `PUT /api/workouts/{id}` - full UI in Phase 7)
- [x] Add week navigation (previous/next week buttons)
- [x] Add week/month view toggle
- [x] Display progress counter (completed/total workouts)
- [x] Add loading states and error handling
- [x] Make it responsive for mobile (Tailwind responsive classes)
- [ ] **Testing**: Test UI with different data scenarios
- [ ] **Testing**: Test responsive design on different screen sizes
- [ ] **Testing**: Test completion toggles and progress updates

**Deliverable**: Functional weekly calendar view UI ✅

**Implementation Notes**:
- Created `WorkoutCard.jsx`, `MonthView.jsx`, and `WeekAheadView.jsx` components
- Created `workoutMapper.js` utility to map database fields to design interface
- Integrated Tailwind CSS with custom color palette
- Connected to backend APIs: `GET /api/workouts/week/{offset}`, `PUT /api/workouts/{id}/complete`, `GET /api/workouts/progress`
- Added week/month navigation implemented
- Edit functionality shows placeholder alert (full implementation in Phase 7)
- Handles empty states and placeholder workouts for days without scheduled workouts

**Design Details** (from Figma export):
- **Color Palette**: 
  - Muted Teal: `#8eb19d` (completed workouts)
  - Carbon Black: `#1e1b18` (text)
  - Almond Silk: `#eacdc2` (background)
  - Persian Blue: `#072ac8` (pending workouts, accents)
  - Rust Brown: `#a44200` (rest days)
- **Components**: 
  - `WeekAheadView.tsx` - Main week view with 7-day grid
  - `WorkoutCard.tsx` - Expandable card with workout details
  - `MonthView.tsx` - Full calendar month view
- **Features**:
  - Expandable workout cards (click to show duration, pace, heart rate zone, intensity, notes)
  - Intensity visualization (progress bar: low 33%, moderate 66%, high 100%)
  - Status indicators (completed ✓, rest -, pending)
  - Progress counter in header
  - Week/month view toggle
  - Previous/next week navigation

**Design Considerations**:
- **Status Mapping**: Design uses `'completed' | 'rest' | 'pending'` but DB uses `is_completed` boolean + `type='rest'` for rest days
- **Missing Fields**: Design shows `intensity` and `heartRateZone` which aren't in database yet
  - Option C: Store in notes or make optional for MVP
- **Day Format**: Design uses day names (Mon, Tue) - need to derive from `scheduled_date`

---

### Phase 6: Monthly Calendar Navigation
**Goal**: Add monthly view and navigation

**Tasks**:
- [x] Create `MonthView.tsx` component (✅ Already in design)
- [x] Implement monthly calendar grid (✅ Already in design)
- [x] Show workout indicators on calendar days (✅ Already in design)
- [x] Add navigation: Week view ↔ Month view (✅ Already in design)
- [ ] **Make calendar dynamic** - Currently hardcoded to January 2026, needs to work for any month/year
- [ ] **Add month navigation functionality** - Previous/next month buttons (UI exists, needs logic)
- [ ] **Make navigation buttons context-aware** - Week view: navigate weeks, Month view: navigate months
- [ ] **Connect to backend API** - `GET /api/workouts/month/{year}/{month}`
- [ ] **Map workouts to calendar dates** - Use `scheduled_date` from API to populate calendar
- [ ] **Click day in month view to jump to that week** - Navigate to week view showing that week
- [x] Visual styling for monthly view (✅ Already in design)
- [ ] **Testing**: Test navigation between views
- [ ] **Testing**: Test month/week transitions
- [ ] **Testing**: Test day click navigation
- [ ] **Testing**: Test month navigation (previous/next)

**Deliverable**: Can navigate between week and month views ✅ (UI complete, needs API integration and dynamic functionality)

**Design Status**:
- ✅ MonthView component exists with full UI
- ✅ Calendar grid layout implemented
- ✅ Workout indicators and status colors
- ✅ Completion toggle and edit buttons in month view
- ⚠️ Calendar generation is hardcoded (needs to be dynamic)
- ⚠️ Month navigation buttons exist but need functionality
- ⚠️ Needs backend API integration

---

### Phase 7: Workout Editing UI
**Goal**: Allow inline editing of workouts

**Tasks**:
- [ ] Design editing interface (modal, inline edit, or side panel)
- [ ] Add "Edit" button/icon on workout cards
- [ ] Create edit form with all workout fields
- [ ] Implement save/cancel functionality
- [ ] Add validation and error handling
- [ ] Update UI immediately after save
- [ ] Consider UX: inline edit vs. modal vs. separate page
- [ ] **Testing**: Test editing workflow end-to-end
- [ ] **Testing**: Test validation and error messages
- [ ] **Testing**: Test cancel functionality

**Deliverable**: Can edit workouts directly in the UI

---

### Phase 8: Plan Selection & Management UI
**Goal**: UI for creating and selecting active plans

**Tasks**:
- [ ] Add "My Plans" section/page
- [ ] Show list of all workout plans
- [ ] Show which plan is currently active
- [ ] Add "Set as Active" button
- [ ] Add "Create New Plan" button (links to chat)
- [ ] Show plan details (goal, duration, start date)
- [ ] Add plan deletion option (optional)

**Deliverable**: Can manage and select workout plans from UI

---

### Phase 9: Polish & Integration
**Goal**: Refine the feature and integrate with existing app

**Tasks**:
- [ ] Integrate week view into main app navigation
- [ ] Add progress summary widgets (completion %, total workouts)
- [ ] Improve visual design and consistency
- [ ] Add empty states (no active plan, no workouts this week)
- [ ] Performance optimization
- [ ] Error handling improvements
- [ ] Add helpful tooltips/instructions
- [ ] **Testing**: End-to-end testing of complete feature
- [ ] **Testing**: User acceptance testing
- [ ] **Testing**: Performance testing

**Deliverable**: Polished MVP integrated into app

---

### Phase 9b: Neon Cloud Database Setup (MOVED TO Phase 1b)
**Note**: This phase has been moved to **Phase 1b** (right after Phase 1) to happen immediately and reduce local Docker resource usage. See Phase 1b above for details.

---

### Phase 10: Strava Auto-Sync (Post-MVP)
**Goal**: Automatically match Strava activities to planned workouts

**Tasks**:
- [ ] Design matching algorithm (date only for MVP, date+distance for advanced)
- [ ] Create endpoint: `POST /api/strava/sync` - Sync and match activities
- [ ] Implement activity-to-workout matching logic
- [ ] Handle edge cases (multiple activities, no match, etc.)
- [ ] Add manual override option (user can manually link activities)
- [ ] Update week view to show matched activities
- [ ] Add "Sync Now" button in UI
- [ ] Add sync status indicators
- [ ] Add advanced matching options (date + distance range)

**Deliverable**: Automatic progress tracking via Strava (Future)

## 🎨 UI/UX Design

### "Week Ahead" View - Weekly Calendar Grid (Selected)

```
┌─────────────────────────────────────────────────────────┐
│  Your Week Ahead                    [Month View] [←] [→]│
│  Progress: 2/5 workouts completed                      │
├─────────────────────────────────────────────────────────┤
│  Mon        Tue       Wed       Thu       Fri    Sat    │
│  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐      │
│  │Easy │   │Rest │   │Tempo│   │Easy │   │Long │      │
│  │Run  │   │     │   │Run  │   │Run  │   │Run  │      │
│  │5km  │   │     │   │8km  │   │5km  │   │15km │      │
│  │[✓]  │   │[-]  │   │[ ]  │   │[ ]  │   │[ ]  │      │
│  └─────┘   └─────┘   └─────┘   └─────┘   └─────┘      │
│                                                         │
│  [Edit] button on each workout card                     │
└─────────────────────────────────────────────────────────┘
```

### Monthly Calendar View

```
┌─────────────────────────────────────────────────────────┐
│  January 2025                    [Week View] [←] [→]  │
├─────────────────────────────────────────────────────────┤
│  Sun  Mon  Tue  Wed  Thu  Fri  Sat                     │
│       1    2    3    4    5    6                       │
│  7    8    9   10   11   12   13                       │
│ 14   15   16   17   18   19   20                       │
│ 21   22   23   24   25   26   27                       │
│ 28   29   30   31                                       │
│                                                         │
│  [●] = Has workouts  [✓] = Week completed              │
│  Click day to jump to that week                        │
└─────────────────────────────────────────────────────────┘
```

### Workout Editing Interface

**Option A: Inline Edit (Recommended for MVP)**
- Click "Edit" on workout card
- Fields become editable inline
- Save/Cancel buttons appear
- Quick and simple

**Option B: Modal Dialog**
- Click "Edit" opens modal
- Full form with all fields
- More space for notes
- Better for complex edits

**Option C: Side Panel**
- Edit panel slides in from side
- Can see context (other workouts)
- Good for desktop, less mobile-friendly

## 🔧 Technical Decisions (Confirmed)

1. **Database**: PostgreSQL (with Google Cloud SQL for future hosting)
2. **ORM**: SQLAlchemy (Python)
3. **Date Handling**: Current calendar week (Monday-Sunday), not plan-based
4. **Matching Algorithm**: Start with date-only for Strava (future), manual completion for MVP
5. **Frontend State**: Polling for updates (simple, WebSockets later if needed)
6. **Editing Interface**: Inline editing for MVP (can upgrade to modal later)

## 📊 Success Metrics

- User can see their week's workouts at a glance
- Can easily mark workouts as completed
- Can edit workout details inline
- Can navigate between week and month views
- Can create and select active workout plans
- Feature is fast and responsive
- Works on mobile (for future online hosting)

## 🚦 MVP Definition

**Minimum Viable Product**:
- ✅ Create workout plan via chat
- ✅ Save plan to database
- ✅ Select a plan as "active"
- ✅ View current calendar week's workouts in grid layout
- ✅ Mark workouts as completed/not completed (checkbox)
- ✅ Edit workouts manually (inline editing)
- ✅ Navigate to monthly calendar view
- ✅ Visual progress indicators (completion count, progress bar)
- ✅ Week navigation (previous/next week)

**Out of Scope for MVP**:
- ❌ Strava auto-sync (moved to post-MVP)
- ❌ Historical weeks view (can add later)
- ❌ Detailed analytics/comparisons
- ❌ Notifications/reminders
- ❌ Multi-user support
- ❌ Advanced Strava matching (date+distance, manual confirmation)

---

## 📝 Implementation Notes

### Database Setup
- **Local Development**: PostgreSQL via Docker (Phase 1)
- **Cloud Database**: Neon (serverless PostgreSQL) - Phase 1b (immediate)
- Use Alembic for migrations (version control for schema)
- Design schema to be extensible for multi-user later
- Neon provides free tier and easy setup (no Docker overhead)

### Cloud Database Options
- **Neon** (Phase 1b): Serverless PostgreSQL, free tier, easy setup - **IMMEDIATE PRIORITY**
- **Google Cloud SQL** (Future): Compatible with PostgreSQL, free tier available
- Both use standard PostgreSQL connection strings
- Plan for connection pooling in production

### Editing Interface Decision
- **Start with inline editing** for MVP simplicity
- Can upgrade to modal or side panel later based on user feedback
- Consider mobile-friendly touch targets

### Date Calculation Logic
- Use Python's `datetime` module
- Calculate current calendar week (Monday = start)
- Calculate scheduled dates: `plan.start_date + (week-1)*7 + (day-1)` days
- Handle edge cases: plan hasn't started yet, plan ended

---

## 🎯 Next Steps

1. **Start with Phase 1**: Set up PostgreSQL database
2. **Review and approve** this plan
3. **Begin implementation** following the phases

Ready to start building! 🚀

