# Workout Coach Architecture Roadmap

> **Last Updated:** February 2026
> **Status:** Phase 6 Complete (multi-user auth, data isolation, preferences, profile page, E2E tests)
> **Mantra:** "Plan your work, work your plan"

---

## Product Vision

Workout Coach is your personal coach that adapts to your context:

- **Training for an event?** It keeps you accountable with a periodized plan (base → build → peak → taper), while letting you adjust based on how you feel.
- **Between goals?** It gives you smart weekly suggestions to stay fit without rigid commitment.

> **Built for runners first.** The initial release focuses on running (5K to marathon). The architecture supports future expansion to triathletes, endurance athletes (cycling, swimming), and strength-focused training.

### Core Principles

1. **Week is the atomic unit** - Everything centers on "this week"
2. **Two modes, one coach** - Training Block (accountability) vs. Maintenance (flexibility)
3. **Friction for plan changes** - Easy to adjust a workout, harder to restructure phases
4. **History is scrollable** - Past weeks viewable, reflection tools come later

---

## Two Operating Modes

| Mode | Trigger | Coach Behavior |
|------|---------|----------------|
| **Training Block** | User sets race goal + date | Periodized plan, phase awareness, accountability |
| **Maintenance** | No active goal | Week-by-week suggestions, casual |

### Training Block Mode
- Follows Lydiard/Daniels/Pfitzinger-style periodization
- Phases: **Base** (aerobic) → **Build** (tempo/threshold) → **Peak** (race-specific) → **Taper** (rest)
- Shows: "Week 8 of 16 - Build Phase"
- Regenerate respects phase constraints

### Maintenance Mode
- No phases, no week numbers
- Fresh suggestions each week based on preferences
- Easy to start a training block when ready

---

## Target Data Model

```
User
├── id, email, name
├── preferences: JSONB
│     {
│       "available_days": ["tue", "thu", "sat", "sun"],
│       "experience_level": "intermediate",
│       "weekly_mileage_comfort": 40
│     }
└── current TrainingBlock (nullable)

TrainingBlock (nullable per user - null = maintenance mode)
├── id
├── user_id (FK)
├── event_name: "Boston Marathon"
├── event_distance: "marathon" | "half" | "10k" | "5k" | custom
├── target_date: 2026-04-20
├── start_date: 2026-01-06
├── total_weeks: 16
├── phase_map: JSONB
│     {
│       "base": [1, 2, 3, 4],
│       "build": [5, 6, 7, 8, 9, 10],
│       "peak": [11, 12, 13],
│       "taper": [14, 15, 16]
│     }
└── status: "active" | "completed" | "abandoned"

Workout
├── id
├── user_id (FK)
├── training_block_id (FK, nullable - null = maintenance workout)
├── date: required
├── week_number: nullable (1-16 for blocks, null for maintenance)
├── phase: nullable ("base" | "build" | "peak" | "taper")
├── workout_type: "easy_run" | "tempo" | "intervals" | "long_run" | "rest" | etc.
├── distance: float (nullable)
├── duration: integer minutes (nullable)
├── notes: text
├── is_completed: boolean
├── completed_at: datetime (nullable)
└── actuals: JSONB (nullable)
      {
        "distance": 6.5,
        "duration": 52,
        "notes": "Felt great, went a bit longer"
      }
```

---

## API Structure (Implemented)

```
# Goal/Block Management
GET    /api/training-block              → current block (or null if maintenance)
POST   /api/training-block              → create new block, LLM generates periodized plan
PUT    /api/training-block/:id          → update block (reschedule race, adjust phases)
PUT    /api/training-block/:id/phases   → adjust phase lengths (with friction confirmation)
DELETE /api/training-block/:id          → end block early (with friction confirmation)

# Weekly View (works both modes)
GET    /api/week                        → current week context + workouts
GET    /api/week?offset=-1              → relative week (negative = past, positive = future)
POST   /api/week/regenerate             → regenerate week
       Body: { "reason": "I'm feeling tired" }  // optional context for LLM

# Response shape for /api/week:
{
  "mode": "training" | "maintenance",
  "week_number": 8,              // null in maintenance
  "phase": "build",              // null in maintenance
  "phase_focus": "Tempo & threshold work",
  "weeks_until_race": 8,         // null in maintenance
  "event_name": "Boston Marathon",
  "workouts": [...]
}

# Workouts
GET    /api/workouts/:id                → single workout details
PUT    /api/workouts/:id                → edit planned workout
POST   /api/workouts/:id/complete       → mark done + log actuals
POST   /api/workouts                    → add ad-hoc workout
DELETE /api/workouts/:id                → remove from week

# User Profile & Preferences
GET    /api/user/profile               → current user's profile + preferences
PUT    /api/user/preferences           → update preferences (available_days, experience_level, weekly_mileage_comfort)

# Training Block Overview (training mode only)
GET    /api/training-block/overview     → full plan visualization
{
  "phases": [
    { "name": "base", "weeks": [1,2,3,4], "status": "completed" },
    { "name": "build", "weeks": [5,6,7,8,9,10], "status": "current" },
    { "name": "peak", "weeks": [11,12,13], "status": "upcoming" },
    { "name": "taper", "weeks": [14,15,16], "status": "upcoming" }
  ],
  "current_week": 8,
  "completion_rate": 0.85,
  "total_miles": 320
}
```

---

## Frontend Architecture (Implemented)

```
App (tabs: Week, Coach, Plans, Profile)
│
├── WeekView (Week tab - both modes) ✅
│     ├── WeekHeader (phase/mode context)
│     ├── WeekNav (prev/next week arrows)
│     ├── DayCards (Mon-Sun)
│     │     └── WorkoutCard (tap to edit/complete)
│     ├── WeekActions ("Regenerate Week" + "Add Workout")
│     └── RegenerateModal (coach-style, optional reason)
│
├── BlockOverview (Plans tab) ✅
│     ├── PhaseTimeline (colored bars: base/build/peak/taper)
│     ├── Progress bar + completion stats
│     └── "End Training Block" (with ConfirmModal)
│
├── GoalSetup (modal — Coach tab when no block) ✅
│     ├── ModeSelect ("Train for a Race" / "Just Staying Fit")
│     ├── RaceDetails (event, distance, date, experience)
│     └── PhasePreview (timeline with +/- adjustment)
│
├── ProfilePage (Profile tab) ✅
│     ├── Account info (name, email — read-only from Google)
│     ├── Training preferences (days, experience, mileage)
│     └── Sign Out button
│
└── Coach tab behavior (state-aware) ✅
      ├── No active block → opens GoalSetup
      └── Active block → navigates to Week + opens RegenerateModal
```

---

## Components Replaced (Phase 5 — All Complete)

| Old Component | Replacement | Status |
|---------------|-------------|--------|
| `WeekAheadView.jsx` (300+ lines) | `WeekView/` + subcomponents | ✅ Deleted |
| `PlanManager/` (entire folder) | `BlockOverview/` | ✅ Deleted |
| `ChatInterface.jsx` | `GoalSetup/` flow | ✅ Deleted |
| `MonthView.jsx` | Removed from nav | ✅ Deleted |

---

## Execution Phases

### Phase 1: Foundation (Quick Wins) ✅
**Goal:** Set up for success without breaking current app

- [x] Design system setup - `styles/tokens.css` with spacing scale
- [x] API constants file - `api/routes.js` with all endpoint paths
- [x] React Query setup - install + configure QueryClient
- [x] New `WeekView.jsx` shell (empty, not connected)

### Phase 2: New Data Model
**Goal:** Backend supports new architecture

- [X] `TrainingBlock` model + Alembic migration
- [X] Update `Workout` model (add `training_block_id`, `phase`, `actuals`)
- [X] `/api/week` endpoint (new unified weekly view)
- [X] `/api/training-block` CRUD endpoints
- [X] Migration script: `WorkoutPlan` → `TrainingBlock`

### Phase 3: New Frontend Core
**Goal:** Replace WeekAheadView with new WeekView

- [X] `WeekHeader` component (phase/mode context)
- [X] `DayCard` component (single day with workouts)
- [X] `WorkoutCard` updates (quick actions)
- [X] `WeekView` assembly (compose header + days + actions)
- [X] Week navigation (prev/next + scroll to past)
- Note: This has not been tested yet

### Phase 4: Goal Setup Flow ✅
**Goal:** Replace chat-based plan generation

- [X] `GoalSetup` modal ("Start Training Block" vs "Stay Fit")
- [X] Race setup flow (event, date, experience → LLM generates block)
- [X] Phase visualization (show phases before confirming)
- [X] Phase adjustment UI (inline +/- controls with constraint validation)
- [X] `POST /api/training-block/:id/generate-workouts` endpoint
- [X] `PeriodizedWorkoutService` — phase-by-phase LLM generation
- [X] `phaseCalculator.js` — default phase distribution + adjustment utility
- Note: Not yet integration-tested against live backend

### Phase 5: Polish & Cleanup ✅
**Goal:** Complete the MVP core loop

- [X] `BlockOverview` screen (phase timeline, stats, end block)
- [X] `RegenerateModal` — coach-style modal with optional reason
- [X] `POST /api/week/regenerate` endpoint with snapshot history (max 3 per week)
- [X] LLM prompt fix: enforce 1 workout per day
- [X] Coach tab state-aware (no block → GoalSetup; active block → regenerate)
- [X] Plans tab renders `BlockOverview` instead of `PlanManager`
- [X] Month tab removed from nav
- [X] Deprecated components deleted (ChatInterface, WeekAheadView, MonthView, PlanManager)
- [X] `week_snapshots` JSONB column on `training_blocks` (migration: `h2i3j4k5l6m7`)

### Phase 6: Multi-user ✅
**Goal:** Production multi-user support

- [X] `User` model with roles (super_admin, admin, beta_tester) + UUID PK
- [X] Google OAuth authentication (`AuthService` with `google.oauth2.id_token` validation)
- [X] Session management (PostgreSQL-backed, 24hr expiry, auto-cleanup)
- [X] `@require_auth` / `@require_admin` decorators gating all endpoints
- [X] Invite code system (single-use, expiry, race-condition safe with row-level locking)
- [X] `InviteCode` model + `InviteCodeService` + admin endpoints
- [X] Database migration: `users` + `invite_codes` tables, `user_id` FK on all data tables
- [X] Seed super_admin with `PENDING_GOOGLE_LINK` for first-login account linking
- [X] All service methods updated to filter by `user_id` (data isolation)
- [X] `GoogleLoginPage` component (Google widget + invite code flow)
- [X] `InviteCodeModal` component (code entry + consent checkbox)
- [X] `App.jsx` wired: `GoogleOAuthProvider` + `GoogleLoginPage` + auth check + logout
- [X] Old `LoginPage` deleted (replaced by `GoogleLoginPage`)
- [X] Admin CLI scripts (`generate_invite_code.py`, `list_invite_codes.py`)
- [X] Cross-user data leakage fixed: 7 service methods + 10 endpoints enforce `user_id` filtering
- [X] `GET /api/user/profile` + `PUT /api/user/preferences` endpoints
- [X] `UserService.update_preferences()` — validates `available_days`, `experience_level`, `weekly_mileage_comfort`
- [X] `ProfilePage.jsx` + CSS — account info, training preferences, sign-out
- [X] Profile tab in desktop nav + mobile bottom nav (logout moved from header)
- [X] E2E test script (`backend/scripts/test_phase6.py`) — data isolation, preferences, session lifecycle

---

## What's Deprecated

**Frontend components deleted** (Phase 5):
- `WeekAheadView.jsx`, `ChatInterface.jsx`, `MonthView.jsx`, `PlanManager/` folder — all removed

**Frontend components deleted** (Phase 6):
- `LoginPage.jsx`, `LoginPage.css` — replaced by `GoogleLoginPage` with Google OAuth

**Backend endpoints kept but deprecated** (legacy data preserved for prompt engineering):
- `POST /api/chat` → replaced by `POST /api/training-block`
- `GET /api/workout-plans` → replaced by `GET /api/training-block`
- `POST /api/workout-plans/:id/activate` → no longer needed (one block per user)

**Models kept:**
- `WorkoutPlan` — kept alongside `TrainingBlock`; `workout_plan_id` nullable on Workout model

---

## LLM Prompt Strategy

### Training Mode Prompt Template
```
User is in week {week_number} of {total_weeks} training for a {event_distance} ({event_name}).
Target date: {target_date}
Current phase: {phase} (focus: {phase_focus}).
User preferences: runs on {available_days}, {experience_level} runner, comfortable with {weekly_mileage} miles/week.
User context: "{regenerate_reason}"  // e.g., "I'm feeling tired"

Generate this week's workouts. Respect the phase focus.
If user mentioned fatigue, slightly reduce intensity but maintain structure.
Return JSON array of workouts with: day, workout_type, distance, duration, notes.
```

### Maintenance Mode Prompt Template
```
User has no active race goal.
Preferences: runs {days_per_week} days/week, {experience_level}, maintain fitness.
Last week: {summary_of_last_week}

Generate a balanced week that maintains fitness without overreaching.
Include variety (easy, tempo, long). No specific phase constraints.
Return JSON array of workouts with: day, workout_type, distance, duration, notes.
```

---

## Design System Notes

### Current Colors (Keep)
```css
--carbon-black: #121212;
--persian-blue: #0047FF;
--pure-white: #FFFFFF;
--success-green: #00C853;
--error-red: #D50000;
--rust-brown: #FF6D00;
```

### Spacing Scale (Add)
```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
```

### Typography Scale (Add)
```css
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
```

---

## Open Questions

1. **Phase customization friction:** What should the confirmation modal say when adjusting phases?
2. **History depth:** How far back should users be able to scroll? (All time? Last 6 months?)
3. **Reflection tools:** What does "better reflection" look like? (Future scope)

---

## Related Linear Issues

- LOC-8: Create User Profiles and Beta Access System (Phase 6)
- LOC-20: Unable to edit when workout is rest ✅ (fixed)
- LOC-22: Include additional workouts per day ✅ (implemented)
- LOC-18: Fix workout card display ✅ (addressed in Phase 3)
- LOC-17: Plan management usability ✅ (superseded by BlockOverview)
