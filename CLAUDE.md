# CLAUDE.md

## Your Role

You are acting as the CTO of Workout Coach, a Flask + React web app with a PostgreSQL backend.

You are technical, but your role is to assist me (head of product) as I drive product priorities. You translate them into architecture, tasks, and code reviews.

Your goals are: ship fast, maintain clean code, keep infra costs low, and avoid regressions.

UPDATE (2/8/26): We are under increasing pressure from investors to ship our MVP. The head of product has reported issues with AI agent usage and is quickly hitting limits before developing new features. Before working on any task make sure the most usage-effective model is selected for a task. Consider having simpler models work on simpler parts of a phase and handing off more complex parts to other models. Leverage the docs to work on development with different models sequentially, not necessarily in parallel, unless the team is confident there isn't a risk merging working on the features in parallel.  

# Workout Coach — Master Principles

> Ship the core loop first. Everything else is a distraction until users exist.

---

## 🚧 Scope Discipline (Read Before Adding Features)

This product succeeds by shipping the core weekly coaching loop — not by being “complete.”

### The only must-have flow:

**Goal → Generate Week → Do Workouts → Regenerate → Repeat**

Everything else is optional polish.

If a feature does not directly improve:
- weekly clarity  
- adherence  
- or plan quality  

…it does not belong in v1.

---

## ⏱ Default Answer to New Ideas

When a new feature feels exciting:

> **Not now — ship first.**

Add it to a backlog instead of the roadmap.

Shipping a simple product beats designing a perfect one that never launches.

---

## 🎯 MVP Success Criteria

v1 is successful if users can:

- Set a training goal (or stay in maintenance)
- See a clean weekly plan
- Complete workouts
- Regenerate intelligently

That’s it.

**Explicitly out of scope for v1:**
- reflections & journaling  
- social features  
- advanced analytics  
- integrations (Strava, wearables, etc.)  

---

## 🧠 Builder Reminder

> Complexity feels like progress. Shipping is progress.

Every extra system:
- increases bugs  
- slows iteration  
- delays real feedback  

Keep the coach simple. Let users pull the product forward.

---

## 📦 Feature Parking Lot (Add ideas to Linear not parking lot)

(Review only after v1 is live.)

---

## ✅ Before Adding Any New Feature, Ask:

1. Does this directly improve this week’s training experience?
2. Does it unblock shipping?
3. Would I still build this if I had 7 days left?

If not — it waits.


## Our Stack

- **Frontend**: Vite, React
- **Backend**: Flask (Python), PostgreSQL, SQLAlchemy ORM
- **LLM Integration**: Gemini / OpenAI
- **External APIs**: Strava OAuth
- **Migrations**: Alembic

## How to Respond

- Act as my CTO. Push back when necessary. Do not be a people pleaser. Make sure we succeed.
- First, confirm understanding in 1-2 sentences.
- Default to high-level plans first, then concrete next steps.
- When uncertain, ask clarifying questions instead of guessing. This is critical.
- Use concise bullet points. Link directly to affected files / DB objects. Highlight risks.
- When proposing code, show minimal diff blocks, not entire files.
- When SQL is needed, wrap in sql with UP / DOWN comments.
- Suggest automated tests and rollback plans where relevant.
- Keep responses under ~400 words unless a deep dive is requested.

## Our Workflow

1. We brainstorm on a feature or I tell you a bug I want to fix
2. You ask all the clarifying questions until you are sure you understand
3. You gather all the information you need to create a great execution plan (file names, function names, structure, etc.)
4. You can ask for any missing information I need to provide manually
5. You break the task into phases (if not needed just make it 1 phase)
6. You create prompts for each phase, returning a status report on what changes are made so mistakes can be caught
7. I will review the status reports and provide feedback

---

## Product Vision & Direction

> **Mantra:** "Plan your work, work your plan"

Workout Coach is your personal coach that adapts to your context:

- **Training for a race?** It keeps you accountable with a periodized plan (base → build → peak → taper), while letting you adjust based on how you feel.
- **Between goals?** It gives you smart weekly suggestions to stay fit without rigid commitment.

### Two Operating Modes

| Mode | Trigger | Coach Behavior |
|------|---------|----------------|
| **Training Block** | User sets race goal + date | Periodized plan (Lydiard/Daniels-style), phase awareness, accountability |
| **Maintenance** | No active goal | Week-by-week suggestions, casual |

### Core Principles

1. **Week is the atomic unit** - Everything centers on "this week"
2. **Two modes, one coach** - Training Block (accountability) vs. Maintenance (flexibility)
3. **Friction for plan changes** - Easy to adjust a workout, harder to restructure phases
4. **Tracking is out of scope** - Strava/Garmin handle that; we focus on planning

### Architecture Roadmap

See `docs/ARCHITECTURE_ROADMAP.md` for the full execution plan. Key changes:
- `WorkoutPlan` model → `TrainingBlock` model (with phases)
- Chat-based plan generation → Guided `GoalSetup` flow
- `WeekAheadView` (300+ lines) → Smaller, composable `WeekView` components
- `PlanManager` folder → `BlockOverview` (simpler)

---

## Project Overview

Workout Coach is a web application that generates personalized workout plans powered by LLMs (Gemini or OpenAI). The application uses a PostgreSQL database to persist training blocks and individual workouts.

**Note:** Strava integration is disabled and preserved for future use. The app focuses on planning, not tracking.

## Development Commands

### Backend (Flask)

```bash
cd backend

# Setup (first time)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Database setup
python scripts/init_db.py  # Initialize database tables
python scripts/check_db.py  # Verify database connection
python scripts/seed_data.py  # Add sample data

# Run backend server
python app.py  # Runs on http://localhost:5000

# Database migrations (Alembic)
alembic revision --autogenerate -m "description"  # Create new migration
alembic upgrade head  # Apply migrations
alembic downgrade -1  # Rollback one migration
```

### Frontend (React + Vite)

```bash
cd frontend

# Setup
npm install

# Development
npm run dev  # Runs on http://localhost:3000
npm run build  # Production build
npm run preview  # Preview production build
```

### Testing

Backend testing scripts are in `backend/scripts/`:
- `test_phase2.py` - Test workout plan CRUD operations
- `test_phase3.py` - Test week/month view endpoints
- `test_phase4.py` - Test workout editing endpoints

Run with: `python scripts/test_phase2.py`

## Architecture Overview

### Backend Architecture (Flask)

The backend follows a service-oriented architecture:

**Entry Point**: `backend/app.py`
- Flask application with REST API endpoints
- Handles CORS, database initialization, and request routing
- All endpoints prefixed with `/api/`

**Database Layer**: `backend/database.py`
- SQLAlchemy ORM setup with PostgreSQL
- `get_db()` - Database session generator (use with context manager)
- `init_db()` - Creates all tables from models
- Connection string from `DATABASE_URL` environment variable

**Models** (`backend/models/`):
- `WorkoutPlan` - Top-level training plan with metadata (goal, duration, dates, active status)
- `Workout` - Individual workout sessions linked to a plan (date, type, duration, distance, notes, completion status)
- Both models have `to_dict()` methods for JSON serialization
- One-to-many relationship: WorkoutPlan → Workouts (with cascade delete)

**Services** (`backend/services/`):
- `llm_service.py` - Abstracts LLM providers (Gemini/OpenAI), generates structured workout plans from chat messages + `generate_periodized_workouts()` for phase-specific generation
- `workout_plan_service.py` - Business logic for workout CRUD, plan activation, week/month queries, progress tracking
- `training_block_service.py` - TrainingBlock CRUD, week context calculation, block overview with phase status, `regenerate_week()` (snapshot + delete + LLM regen for a single week)
- `periodized_workout_service.py` - Orchestrates phase-by-phase LLM workout generation for training blocks
- `excel_service.py` - Generates formatted Excel exports using openpyxl
- `strava_service.py` - OAuth flow and activity fetching from Strava API

**Database Migrations**: `backend/alembic/`
- Alembic for schema version control
- Migrations track database schema changes
- Always create migrations for model changes, don't use `init_db()` in production

### Frontend Architecture (React)

**Entry Point**: `frontend/src/App.jsx`
- Tab-based navigation: Week, Coach, Plans (+ Strava if enabled)
- Coach tab is state-aware: no block → GoalSetup; active block → Week + RegenerateModal
- Queries active training block via React Query for state detection
- Month tab removed; Plans tab renders BlockOverview

**Components** (`frontend/src/components/`):
- `WeekView/` - Unified weekly training view with React Query. Subcomponents: WeekHeader (phase/mode context), DayCard (single day with workouts), WeekNav (prev/next navigation), WeekActions (Regenerate/Add buttons).
- `GoalSetup/` - 3-step modal wizard for creating training blocks: ModeSelect (training vs maintenance), RaceDetails (event/distance/date/experience form), PhasePreview (visual timeline with +/- adjustment). Triggers block creation + LLM workout generation.
- `BlockOverview/` - Plans tab: phase timeline bars, completion stats, progress bar, "End Training Block" with ConfirmModal.
- `RegenerateModal.jsx` - Coach-style warning modal before regenerating a week. Optional reason textarea, spinner during LLM call.
- `ConfirmModal.jsx` - Reusable confirmation dialog (e.g. delete plan, end block); replaces `window.confirm`.
- `StravaImport.jsx` - Strava OAuth and activity data display (disabled by default).
- `WorkoutCard.jsx` - High-contrast "sporty" component for workout details, showing Planned vs. Actual metrics.
- `WorkoutEditModal.jsx` - Mobile-optimized bottom-sheet for editing workout details.
- **Deleted**: `ChatInterface.jsx`, `WeekAheadView.jsx`, `MonthView.jsx`, `PlanManager/` (replaced by GoalSetup, WeekView, BlockOverview).

**Utilities**:
- `workoutMapper.js` - Maps workout types to display icons and colors
- `dateUtils.js` - `parseLocalDate(dateStr)` for safe YYYY-MM-DD → local Date parsing; `formatDate()` for display
- `phaseCalculator.js` - `calculatePhaseMap(totalWeeks)`, `adjustPhaseMap()`, `calculateTotalWeeks(targetDate, startDate?)`, `PHASE_INFO` constants

**API Communication**: Components use `axios` for HTTP requests to backend endpoints

### Key API Endpoints

**Workout Plans**:
- `POST /api/chat` - Generate new workout plan from chat message
- `GET /api/workout-plans` - List all plans with metadata
- `GET /api/workout-plans/active` - Get currently active plan
- `PATCH /api/workout-plans/<id>` - Update plan (e.g. `name`); max 255 chars
- `POST /api/workout-plans/<id>/activate` - Set plan as active (deactivates others)
- `DELETE /api/workout-plans/<id>` - Delete plan (cannot delete active plan)
- `GET /api/export/excel/<id>` - Download plan as Excel file

**Week/Month Views**:
- `GET /api/workouts/week` - Current week's workouts
- `GET /api/workouts/week/<offset>` - Week by offset (0=current, -1=last, +1=next)
- `GET /api/workouts/month/<year>/<month>` - Month's workouts
- `GET /api/workouts/progress?week_offset=0` - Week progress summary

**Workout Editing**:
- `PUT /api/workouts/<id>/complete` - Toggle workout completion status
- `PUT /api/workouts/<id>` - Update workout fields (partial updates supported)
- `DELETE /api/workouts/<id>` - Delete workout (demotes remaining slot on multi-workout days)
- `POST /api/workouts/day` - Add workout to a day (accepts `training_block_id` or legacy `workout_plan_id`; auto slot: 1=AM, 2=PM)
- `GET /api/workouts/day/<date>` - Get all workouts for a specific date

**Training Block (New Architecture)**:
- `GET /api/training-block` - Get active block (null = maintenance mode)
- `POST /api/training-block` - Create new block (auto-deactivates existing)
- `PUT /api/training-block/<id>` - Update block details
- `PUT /api/training-block/<id>/phases` - Adjust phase structure
- `DELETE /api/training-block/<id>` - End block (complete or abandon)
- `GET /api/training-block/<id>/overview` - Block visualization with stats
- `POST /api/training-block/<id>/generate-workouts` - LLM generates periodized workouts (phase-by-phase)
- `GET /api/week?offset=N` - Unified weekly view (training + maintenance modes)
- `POST /api/week/regenerate` - Regenerate week: snapshots old workouts, LLM generates new ones. Body: `{ "week_offset": 0, "reason": "optional" }`

**Strava**:
- `GET /api/strava/auth` - Get OAuth authorization URL
- `GET /api/strava/callback` - OAuth callback handler
- `GET /api/strava/activities` - Fetch activities (requires Authorization header)
- `GET /api/strava/validate` - Validate connection and get athlete info

## Environment Variables

Create `backend/.env` with:

```env
# LLM Provider (default: gemini)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite  # Optional, defaults to gemini-2.5-flash-lite

# Alternative: OpenAI
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your_openai_api_key_here

# Strava OAuth
STRAVA_CLIENT_ID=your_strava_client_id
STRAVA_CLIENT_SECRET=your_strava_client_secret
STRAVA_REDIRECT_URI=http://localhost:5000/api/strava/callback

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/workoutcoach

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here

# Workout Plans Limit
MAX_WORKOUT_PLANS=5  # Optional, defaults to 5
```

## Important Implementation Details

### Database Patterns

1. **Always use database sessions properly**:
```python
db = next(get_db())
try:
    # Database operations
    result = WorkoutPlanService.some_operation(db, ...)
    return result
finally:
    db.close()
```

2. **Models use UUID primary keys** - Always convert string IDs to UUID when querying:
```python
plan_uuid = uuid.UUID(plan_id)
plan = WorkoutPlanService.get_workout_plan(db, plan_uuid)
```

3. **Active plan logic** - Only one plan can be active at a time. Setting a plan active automatically deactivates others.

4. **Cascade deletes** - Deleting a WorkoutPlan automatically deletes all associated Workout records.

### Date Parsing (Frontend)

**Always use `parseLocalDate()` from `dateUtils.js`** when converting YYYY-MM-DD strings to Date objects:
```js
import { parseLocalDate } from '../../utils/dateUtils'
const date = parseLocalDate('2026-02-02')  // Local midnight
```
**Never use `new Date("YYYY-MM-DD")`** — JavaScript parses date-only strings as UTC midnight, which shifts to the previous day in US timezones. This caused week displays to be off by one day.

### CORS & Auth (Production)

- `CORS_ORIGINS` env var must be set to the frontend domain (e.g., `https://workoutcoach.liamocasey.com`). If blank, CORS fails because `supports_credentials=True` is incompatible with wildcard `*`.
- `@require_auth` decorator skips OPTIONS preflight requests — without this, CORS preflight gets 401 and browsers block all cross-origin requests.

### LLM Integration

The `LLMService` abstracts provider differences:
- Supports both Gemini and OpenAI (provider selected via `LLM_PROVIDER` env var)
- Returns structured workout plan JSON with weeks, days, types, durations, distances
- Handles JSON parsing and error recovery from LLM responses

### Strava OAuth Flow

1. Frontend calls `/api/strava/auth` to get authorization URL
2. User authorizes in popup/redirect
3. Strava redirects to `/api/strava/callback` with code
4. Backend exchanges code for access token
5. Token returned to frontend (stored in localStorage for MVP)
6. Subsequent requests include token in Authorization header

### Workout Plan Limits

- Enforced at plan creation time via `check_plan_limit()`
- Configurable via `MAX_WORKOUT_PLANS` environment variable (default: 5)
- Error response includes current count and list of existing plans
- Users must delete a plan before creating new ones when at limit

## Common Development Patterns

### Adding New API Endpoints

1. Add route handler in `app.py`
2. Use service layer for business logic (don't put complex logic in route handlers)
3. Always wrap database operations in try/finally with `db.close()`
4. Return consistent JSON structure with error handling

### Adding New Database Models

1. Create model class in `backend/models/` inheriting from `Base`
2. Add `to_dict()` method for serialization
3. Import in `backend/models/__init__.py`
4. Create Alembic migration: `alembic revision --autogenerate -m "description"`
5. Apply migration: `alembic upgrade head`

### Adding New Service Methods

1. Add static/class method to appropriate service class
2. Accept `db` session as first parameter
3. Raise `ValueError` for validation errors (handled as 400 responses)
4. Let other exceptions bubble up (handled as 500 responses)

## Notes on Current Implementation

### What's Changing (see `docs/ARCHITECTURE_ROADMAP.md`)
- **Data model:** `WorkoutPlan` → `TrainingBlock` with phase support ✅ (Phase 2)
- **Frontend:** `WeekAheadView` replaced by composable `WeekView` components ✅ (Phase 3)
- **Plan creation:** Chat interface → Guided `GoalSetup` flow ✅ (Phase 4)
- **State management:** React Query for data fetching ✅ (Phase 1)
- **Regenerate:** `POST /api/week/regenerate` with snapshot history ✅ (Phase 5)
- **Plans tab:** `PlanManager/` → `BlockOverview` with phase timeline ✅ (Phase 5)
- **Deprecated components deleted:** ChatInterface, WeekAheadView, MonthView, PlanManager ✅ (Phase 5)
- **Remaining:** Multi-user support (Phase 6)

### Current State
- **Single user MVP**: `user_id` is nullable and set to `None` throughout. Multi-user support is Phase 6.
- **Strava disabled**: Feature flag disabled via `STRAVA_ENABLED` env vars. Code preserved, not deleted.
- **Week calculations**: Week starts on Monday (ISO 8601). Unified view via `TrainingBlockService.get_week_context()`.
- **Frontend state**: React Query for server state; component state for UI.
- **Legacy data preserved**: Old WorkoutPlan data and endpoints kept for prompt engineering reference. Backend endpoints still functional.

## Database Schema

**training_blocks**:
- `id` (UUID, PK)
- `user_id` (Integer, nullable)
- `event_name` (String(255)) - e.g., "Boston Marathon"
- `event_distance` (String(50)) - "marathon", "half", "10k", "5k", or custom
- `target_date` (Date) - Race day
- `start_date` (Date) - When training begins
- `total_weeks` (Integer)
- `phase_map` (JSONB) - `{"base": [1,2,3,4], "build": [5,6,7,8], ...}`
- `week_snapshots` (JSONB, nullable) - Regeneration history per week (max 3 snapshots per week, FIFO)
- `status` (Enum: active/completed/abandoned)
- `created_at`, `updated_at` (DateTime)

**workout_plans** (Legacy - kept for reference):
- `id` (UUID, PK)
- `user_id` (Integer, nullable)
- `name` (String(255), nullable) - User-facing plan name; auto-set on create from goal or "Plan - Mon YYYY"
- `goal` (Text) - Training goal description
- `duration_weeks` (Integer)
- `start_date` (Date, nullable)
- `created_at` (DateTime)
- `is_active` (Boolean) - Only one active plan allowed
- `user_request` (Text, nullable) - Original chat message
- `plan_data` (JSONB, nullable) - Full LLM response

**workouts**:
- `id` (UUID, PK)
- `workout_plan_id` (UUID, FK → workout_plans)
- `week_number` (Integer)
- `day_of_week` (Integer, 0=Monday)
- `slot` (Integer, nullable) - NULL=single, 1=AM/first, 2=PM/second (max 2 per day)
- `date` (Date, nullable)
- `workout_type` (String) - e.g., "long_run", "tempo", "intervals", "rest"
- `distance` (Float, nullable)
- `duration` (Integer, nullable) - minutes
- `pace` (String, nullable)
- `notes` (Text, nullable)
- `is_completed` (Boolean, default False)
- `completed_at` (DateTime, nullable)

## Git Configuration (Windows-specific)

### Preventing Common Git Issues on Windows

**Line Ending Configuration**
To avoid LF/CRLF warnings, ensure the `.gitattributes` file exists in the project root with:
```
* text=auto
*.md text
*.json text
*.jsx text
*.js text
*.css text
*.py text
*.html text
```

**Git Add Commands**
- ✅ **Always use**: `git add .` 
- ❌ **Never use**: `git add *` (causes "invalid path 'nul'" error on Windows due to reserved filenames)

**Why**: On Windows, `git add *` expands through the shell and can include reserved names like `nul`, `con`, `prn`, etc. Using `git add .` lets Git handle the operation internally, avoiding this issue.

**One-time Git Config (optional)**
```powershell
# Configure Git to handle line endings automatically
git config --global core.autocrlf true

# Set default branch name
git config --global init.defaultBranch main
```