# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Workout Coach is a locally hosted web application that generates personalized workout plans through a chat interface powered by LLMs (Gemini or OpenAI) and integrates with Strava for activity data import. The application uses a PostgreSQL database to persist workout plans and individual workouts.

**Stack**: Flask (Python) backend + React (Vite) frontend + PostgreSQL database

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
- `llm_service.py` - Abstracts LLM providers (Gemini/OpenAI), generates structured workout plans from chat messages
- `workout_plan_service.py` - Business logic for workout CRUD, plan activation, week/month queries, progress tracking
- `excel_service.py` - Generates formatted Excel exports using openpyxl
- `strava_service.py` - OAuth flow and activity fetching from Strava API

**Database Migrations**: `backend/alembic/`
- Alembic for schema version control
- Migrations track database schema changes
- Always create migrations for model changes, don't use `init_db()` in production

### Frontend Architecture (React)

**Entry Point**: `frontend/src/App.jsx`
- Tab-based navigation between three main views
- Manages active tab state (week/chat/strava)

**Components** (`frontend/src/components/`):
- `WeekAheadView.jsx` - Calendar view showing current week's workouts, completion tracking, navigation
- `ChatInterface.jsx` - LLM chat for workout plan generation, plan management (view/activate/delete), Excel export
- `StravaImport.jsx` - Strava OAuth and activity data display
- `WorkoutCard.jsx` - Reusable component for displaying workout details
- `MonthView.jsx` - Calendar month view of workouts (currently in development)

**Utilities**:
- `workoutMapper.js` - Maps workout types to display icons and colors

**API Communication**: Components use `axios` for HTTP requests to backend endpoints

### Key API Endpoints

**Workout Plans**:
- `POST /api/chat` - Generate new workout plan from chat message
- `GET /api/workout-plans` - List all plans with metadata
- `GET /api/workout-plans/active` - Get currently active plan
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

- **Single user MVP**: `user_id` is nullable and set to `None` throughout. Multi-user support is future work.
- **Strava activities**: Still stored in-memory (`imported_activities` list in app.py). Not yet migrated to database.
- **Week calculations**: Week starts on Monday (ISO 8601). `get_week_start_end()` and `get_week_by_offset()` in `WorkoutPlanService`.
- **Frontend state**: Minimal state management, mostly component-level state. No Redux or global state library.
- **Excel export**: Uses `openpyxl` to create formatted workbooks with workout schedules by week.

## Database Schema

**workout_plans**:
- `id` (UUID, PK)
- `user_id` (Integer, nullable)
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
- `date` (Date, nullable)
- `workout_type` (String) - e.g., "long_run", "tempo", "intervals", "rest"
- `distance` (Float, nullable)
- `duration` (Integer, nullable) - minutes
- `pace` (String, nullable)
- `notes` (Text, nullable)
- `is_completed` (Boolean, default False)
- `completed_at` (DateTime, nullable)
