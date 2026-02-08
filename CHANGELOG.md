# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `CoachMenu` component — bottom-sheet (mobile) / modal (desktop) with 3 options: Regenerate Week, Start New Block, Adjust Phases
- Mobile day-picker in `WeekView` — horizontal scrollable day pills + single DayCard hero below 768px
- `.week-view__empty-cta` CSS for maintenance mode CTA button

### Changed
- `WeekHeader` simplified — single-line "Week 8/16 . Build Phase", removed phase focus badge and lucide icons, reduced padding
- `WeekHeader` maintenance mode — "This Week" + date inline, "Just Staying Fit" subtitle
- Coach tab now opens `CoachMenu` (3 options) instead of directly triggering RegenerateModal
- Maintenance empty state messaging — "Maintenance Mode" with friendlier copy

### Fixed
- **Critical**: `get_week_context()` leaked ALL workouts by date range — now filters by `training_block_id` (training mode) or orphan workouts only (maintenance mode)

### Added (prior)
- **Architecture Roadmap Phase 5: Polish & Cleanup**
  - `POST /api/week/regenerate` endpoint — snapshots existing workouts (max 3 per week, FIFO), deletes old, LLM generates fresh week respecting phase
  - `week_snapshots` JSONB column on `training_blocks` (migration: `h2i3j4k5l6m7`)
  - `TrainingBlockService.regenerate_week()` — orchestrates snapshot + delete + generate for a single week
  - `RegenerateModal.jsx` + CSS — coach-style modal with optional reason textarea, spinner, Escape/backdrop close
  - `BlockOverview/` component — phase timeline bars, completion stats, progress bar, "End Training Block" action
  - Coach tab is now **state-aware**: no block → GoalSetup; active block → Week tab + RegenerateModal
  - Plans tab renders `BlockOverview` instead of PlanManager

### Changed
- **App.jsx**: Removed Month tab from nav; removed ChatInterface/PlanManager/StravaImport/WeekAheadView imports; added `useQuery` for active block detection; lifted `showRegenerate` state to App and passed as props to WeekView
- **WeekView.jsx**: Wired regenerate mutation (`useMutation` → `POST /api/week/regenerate`); accepts `showRegenerate`/`setShowRegenerate` props; added toast feedback on success/error
- **WeekActions.jsx**: Now receives `isRegenerating` prop to show spinner during regeneration
- **LLM prompt** (`llm_service.py`): Added "EXACTLY ONE workout per day, 7 per week" rules to prevent multi-workout-per-day generation
- **routes.js**: Fixed `TRAINING_BLOCK.OVERVIEW` to accept block ID; marked CHAT and WORKOUT_PLANS sections as `(Deprecated)`

### Removed
- `ChatInterface.jsx` + CSS — replaced by GoalSetup
- `WeekAheadView.jsx` — replaced by WeekView
- `MonthView.jsx` — removed from nav
- `PlanManager/` folder (PlanManager, PlanCard, PlanList, ActivePlanView, PlanUpload) — replaced by BlockOverview
- Month tab from desktop and mobile navigation

### Fixed
- LLM generating 4 workouts per day instead of 1 (prompt constraint added)
- "Regenerate Week" button was a no-op (now functional with snapshot + LLM regen)
- Coach tab always opened GoalSetup even with active block (now state-aware)
- Plans tab showed legacy PlanManager (now shows BlockOverview)
- Week number calculation for regeneration when block `start_date` falls mid-calendar-week

- **Architecture Roadmap Phase 4: Goal Setup Flow**
  - `GoalSetup/GoalSetup.jsx` - 3-step modal wizard (Mode Select → Race Details → Phase Preview → Generate)
  - `GoalSetup/ModeSelect.jsx` - "Train for a Race" vs "Just Staying Fit" card selection
  - `GoalSetup/RaceDetails.jsx` - Form: event name, distance dropdown, date picker (4-52 week validation), experience level radio cards
  - `GoalSetup/PhasePreview.jsx` - Colored phase timeline bar, week ranges, inline +/- phase adjustment with constraints
  - `GoalSetup/GoalSetup.css` - Full modal styling (follows ConfirmModal patterns)
  - `utils/phaseCalculator.js` - `calculatePhaseMap(totalWeeks)` distributes weeks across base/build/peak/taper; `adjustPhaseMap()` for constrained adjustment; `PHASE_INFO` display constants
  - `backend/services/periodized_workout_service.py` - Orchestrates phase-by-phase LLM workout generation, calculates `scheduled_date`, bulk-inserts workouts
  - `LLMService.generate_periodized_workouts()` - Phase-specific LLM prompting (distance, focus, experience level); supports Gemini and OpenAI
  - `POST /api/training-block/:id/generate-workouts` - Endpoint: generates periodized workouts for a block (accepts `experience_level`)
  - `GENERATE_WORKOUTS` route added to `api/routes.js`
  - "Start Training Block" CTA button in WeekAheadView and WeekView empty states
- **Architecture Roadmap Phase 3: Frontend Core (WeekView Components)**
  - `WeekHeader.jsx` + CSS - Context-aware header (training mode: "Week 8 · Build Phase" with countdown; maintenance: simplified)
  - `DayCard.jsx` + CSS - Single day container with 0-2 workouts, AM/PM slot support, today highlight
  - `WeekNav.jsx` + CSS - Week navigation (prev/next buttons, current week indicator, date range display)
  - `WeekActions.jsx` + CSS - Footer actions (Regenerate Week button, Add Workout button, loading states)
  - `WeekView.jsx` fully implemented with React Query (`useQuery` for `/api/week`, `useMutation` for complete/add)
  - Phase badges on WorkoutCard (base/build/peak/taper with phase-specific colors)
  - Actuals vs Planned metrics display on WorkoutCard
  - Loading, error, and empty state handling in WeekView
- **Architecture Roadmap Phase 1: Foundation**
  - `frontend/src/styles/tokens.css` - Design system tokens (spacing scale, typography, borders, shadows, z-index)
  - `frontend/src/api/routes.js` - Centralized API endpoint paths with query param builder
  - `frontend/src/api/queryClient.js` - React Query v5 config with sensible defaults + query key factories
  - `frontend/src/components/WeekView/` - Shell component for new unified week view (Phase 3 implementation)
  - `@tanstack/react-query@^5` added to frontend dependencies
- **Training Block Architecture (Phase 2)**
  - New `TrainingBlock` model: event-based training with periodization phases (base/build/peak/taper)
  - `training_blocks` table with event_name, event_distance, target_date, phase_map (JSONB), status
  - Updated `Workout` model: added `training_block_id` (FK), `phase`, `actuals` (JSONB for logged data)
  - `TrainingBlockService`: manages blocks, calculates current week/phase, provides week context
  - **New Endpoints:**
    - `GET /api/training-block` - Get active block (null = maintenance mode)
    - `POST /api/training-block` - Create new training block
    - `PUT /api/training-block/:id` - Update block details
    - `PUT /api/training-block/:id/phases` - Adjust phase structure
    - `DELETE /api/training-block/:id` - End block (complete or abandon)
    - `GET /api/training-block/:id/overview` - Full block visualization with stats
    - `GET /api/week?offset=N` - Unified weekly view (works in training & maintenance modes)
  - Alembic migration: `g1h2i3j4k5l6_add_training_blocks.py`
- **Multiple Workouts Per Day (LOC-22)**
  - New `slot` column on workouts table: NULL=single, 1=AM, 2=PM (max 2 per day)
  - `POST /api/workouts/day` - Add workout to a day with auto slot assignment
  - `DELETE /api/workouts/<id>` - Delete workout (demotes remaining to single slot)
  - `GET /api/workouts/day/<date>` - Get all workouts for a specific date
  - Frontend: Day picker shows "+1" badge when day has 2 workouts
  - Frontend: Desktop grid stacks workout cards with AM/PM indicators
  - Frontend: "Add Workout" button on days with < 2 workouts
  - MonthView: Calendar cells display multiple workouts with AM/PM labels
- **Plan Management Usability (LOC-13)**
  - Workout plan `name` field: backend column + migration with backfill (goal or "Plan - Mon YYYY"), auto-name on create
  - PATCH `/api/workout-plans/<id>` to update plan name (max 255 chars)
  - Plans tab: two-level flow (default = Manage Active Plan; "Manage All Plans" shows all plans grid); tab label "Plans" with ClipboardList icon
  - Inline plan name editing in PlanCard and ActivePlanView (pencil, Enter/Escape)
  - `ConfirmModal.jsx` – reusable confirmation dialog; plan delete uses it instead of `window.confirm`
  - `frontend/src/utils/dateUtils.js` – shared `formatDate()` used by PlanCard and ActivePlanView
- **Authentication System**: Simple username/password auth with session management
  - Backend: `auth_service.py` with session tokens, 24h expiry, `@require_auth` decorator
  - Frontend: `LoginPage.jsx` with form, auth state in `App.jsx`
  - Endpoints: `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/check`
  - Disabled in dev if `AUTH_USERNAME`/`AUTH_PASSWORD` not set
- **Production Deployment Config (LOC-7)**
  - Backend Dockerfile: Python 3.11-slim, gunicorn, non-root user
  - Frontend Dockerfile: Multi-stage build with nginx
  - `docker-compose.production.yml` for local prod testing
  - `env.production.template` with documented variables
- **GitHub Actions CI/CD** (`.github/workflows/deploy.yml`)
  - Auto-deploys on push to main
  - Builds Docker on GitHub (no local Docker needed)
  - Backend → AWS Lightsail container service
  - Frontend → S3 static site
  - CloudFront cache invalidation (optional)
  - **Database migrations**: Runs `alembic upgrade head` before deployment
- **Migration Helper Script** (`backend/scripts/run_migrations.py`)
  - Manual migration tool for local or production use
  - Flags: `--status`, `--history`, `--verify`
  - Auto-verifies expected tables after migration
- **AWS Infrastructure**
  - Lightsail container service: `workout-coach-backend`
  - S3 bucket: `workoutcoach-frontend` (public static hosting)
  - IAM user with AdministratorAccess for deployments
- **Environment-Driven URLs**: `FRONTEND_URL`, `CORS_ORIGINS`, `VITE_API_URL`
- **Mobile-First UI Redesign**: Fully responsive, high-contrast "sporty" interface inspired by professional training tools.
- **Horizontal Day Picker**: New scrollable navigation for the week view on mobile.
- **Today Hero Section**: Dynamic dashboard element highlighting the current day's training with large metrics.
- **Side-by-Side Metrics**: Workout cards now show "Planned vs. Actual" durations and distances.
- **Bottom-Sheet Edit View**: Mobile-optimized modal for updating workout details.
- **Quick Action Buttons**: Touch-friendly buttons (min 44x44px) for one-tap completion and editing.
- **Desktop Navigation**: Horizontal tab bar below header for screens ≥769px (Week, Month, Coach, Strava, Settings)
- **CloudFront CDN**: SSL termination and caching for frontend at `workoutcoach.liamocasey.com`

### Changed
- **App.jsx**: "Coach" tab now opens GoalSetup modal instead of ChatInterface; added `showGoalSetup` state; `Target` icon replaces `MessageSquare` for Coach nav
- **WeekAheadView.jsx**: Accepts `onStartTraining` prop; empty state CTA says "Start Training Block" and opens GoalSetup
- **WeekView.jsx**: Accepts `onStartTraining` prop; empty state updated with `Target` icon and "Start Training Block" CTA
- **WorkoutCard.jsx**: Added `phase` and `actuals` props for training block support; displays phase badge in header
- **WorkoutCard.css**: Added phase badge styling with phase-specific colors (base=sage, build=blue, peak=orange, taper=green)
- **WeekView/index.js**: Updated exports to include all new subcomponents (WeekHeader, DayCard, WeekNav, WeekActions)
- `main.jsx` now wraps App with `QueryClientProvider` for React Query support
- `index.css` imports design tokens from `styles/tokens.css`
- **Workout model**: `workout_plan_id` now nullable (supports new architecture alongside legacy)
- **Strava Feature Flag (LOC-23)**: Strava integration now disabled by default via `STRAVA_ENABLED` (backend) and `VITE_STRAVA_ENABLED` (frontend) env vars. All code intact for future re-enablement.
- **Plans tab flow**: Manage Active Plan is now the default view; "Manage All Plans" button opens the full plan list; "Back to Active Plan" returns from All Plans
- **Plans tab**: Nav label "Settings" → "Plans"; icon Settings → ClipboardList (key remains `plans`)
- **Delete plan**: Confirmation via in-app modal (ConfirmModal) instead of browser `window.confirm`
- **Alembic**: Replaced manual name migration with `c4e8f2b3d5a6_add_name_to_workout_plans.py` (proper 12-char revision ID, same backfill)
- All API routes now protected with `@require_auth` (except `/api/health`)
- CORS config reads from `CORS_ORIGINS` env var (comma-separated)
- Strava OAuth callback uses `FRONTEND_URL` env var
- Added `gunicorn==21.2.0` to backend requirements
- **Visual Theme**: Transitioned from muted tones to a high-contrast palette (Sporty Blue and Carbon Black).
- **Typography**: Updated to bold, high-glancability fonts (Inter) for better readability during training.
- **Workout Card Layout**: Prioritized Duration as the primary metric in a more minimalist, professional layout.
- **Navigation**: Moved main navigation to a fixed bottom bar on mobile for better ergonomics.
- **Global Styles**: Updated `index.css` and `App.css` with a modernized design system and CSS variables.

### Security
- **Strava routes (LOC-23)**: Return 404 (not 403) when feature disabled to prevent route enumeration
- Session tokens use `secrets.token_urlsafe(32)` for cryptographic randomness
- Constant-time credential comparison via `secrets.compare_digest`
- Auth cookies: `httponly=True`, `secure=True` (production), `samesite=Lax`
- Non-root user in backend Docker container

### Fixed
- **Rest Day Editing (LOC-20)**: Rest days can now be edited on mobile and desktop
  - Edit button always visible for rest days (previously hidden on mobile)
  - Mark Complete button hidden (not just disabled) for rest days
  - Applies to WeekAheadView hero, WorkoutCard, and MonthView
- **Critical**: Fixed blank screen bug caused by undefined `swipeHandlers` in WeekAheadView - `useSwipeable` hook was imported but never called.
- **LOC-21**: Fixed NaN display in mobile day picker - now shows workout duration (e.g., "30min"), distance (e.g., "6km"), "Rest", or "--" instead of broken date numbers.
- Improved mobile responsiveness across all main views.
- Optimized touch targets for accessibility and ease of use on small screens.
- Removed unnecessary container and header borders in Week view for cleaner UI.

