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

### Phase 2: Workout Plan Management API
**Goal**: Build API for creating, selecting, and managing workout plans

**Tasks**:
- [ ] Update `POST /api/chat` to save plan to database
- [ ] Create endpoint: `GET /api/workout-plans` - List all plans
- [ ] Create endpoint: `GET /api/workout-plans/{id}` - Get specific plan
- [ ] Create endpoint: `POST /api/workout-plans/{id}/activate` - Set plan as active
- [ ] Create endpoint: `GET /api/workout-plans/active` - Get current active plan
- [ ] Add validation (only one active plan at a time)
- [ ] Add plan start_date calculation/assignment
- [ ] Test plan creation and activation flow

**Deliverable**: Can create plans and set one as active

---

### Phase 3: Week View Backend API
**Goal**: Build API endpoints to support the week calendar view

**Tasks**:
- [ ] Create endpoint: `GET /api/workouts/week` - Get workouts for current calendar week
- [ ] Create endpoint: `GET /api/workouts/week/{week_offset}` - Get specific week (0=current, -1=last, +1=next)
- [ ] Create endpoint: `GET /api/workouts/month/{year}/{month}` - Get workouts for a month
- [ ] Create endpoint: `PUT /api/workouts/{id}/complete` - Toggle completion status
- [ ] Create endpoint: `GET /api/workouts/progress` - Get progress summary for week
- [ ] Add date calculation logic (determine calendar week, scheduled dates)
- [ ] Add completion status to workout responses
- [ ] Handle edge cases (no active plan, plan hasn't started yet)

**Deliverable**: Backend API ready to serve week/month view data

---

### Phase 4: Workout Editing API
**Goal**: Allow manual editing of workout details

**Tasks**:
- [ ] Create endpoint: `PUT /api/workouts/{id}` - Update workout details
- [ ] Add validation for workout fields (type, distance, pace, notes)
- [ ] Handle partial updates (only update fields provided)
- [ ] Add `updated_at` timestamp tracking
- [ ] Test editing functionality

**Deliverable**: Workouts can be edited via API

---

### Phase 5: "Week Ahead" Frontend - Calendar View
**Goal**: Build the visual weekly calendar dashboard

**Tasks**:
- [ ] Design mockup/wireframe for week calendar view
- [ ] Create new React component: `WeekAheadView.jsx`
- [ ] Implement weekly calendar grid layout (Mon-Sun)
- [ ] Display workout cards with key info (type, distance, pace)
- [ ] Add completion checkbox/toggle per workout
- [ ] Add progress indicators (completed count, visual progress bar)
- [ ] Add visual styling (color coding by workout type)
- [ ] Add loading states and error handling
- [ ] Make it responsive for mobile

**Deliverable**: Functional weekly calendar view UI

---

### Phase 6: Monthly Calendar Navigation
**Goal**: Add monthly view and navigation

**Tasks**:
- [ ] Create `MonthView.jsx` component
- [ ] Implement monthly calendar grid
- [ ] Show workout indicators on calendar days
- [ ] Add navigation: Week view ↔ Month view
- [ ] Add week navigation (previous/next week)
- [ ] Add month navigation (previous/next month)
- [ ] Click day in month view to jump to that week
- [ ] Visual styling for monthly view

**Deliverable**: Can navigate between week and month views

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

**Deliverable**: Polished MVP integrated into app

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
- Use PostgreSQL locally for development
- Consider Docker for easy PostgreSQL setup
- Use Alembic for migrations (version control for schema)
- Design schema to be extensible for multi-user later

### Google Cloud SQL Considerations
- Compatible with PostgreSQL
- Free tier: Cloud SQL (shared-core instance)
- Can use Cloud SQL Proxy for local development
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

