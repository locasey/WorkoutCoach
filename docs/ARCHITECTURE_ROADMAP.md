# Workout Coach Architecture Roadmap

> **Last Updated:** February 2026
> **Status:** Phase 1 Complete ✅ (20% overall)
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

## Target API Structure

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

## Target Frontend Architecture

```
App
│
├── WeekView (HOME - both modes)
│     ├── WeekHeader
│     │     - Training: "Week 8 · Build Phase · 8 weeks to Boston"
│     │     - Maintenance: "This Week"
│     ├── DayCards (Mon-Sun)
│     │     └── WorkoutCard (tap to edit/complete)
│     ├── WeekActions
│     │     - "Regenerate Week" (with optional context)
│     │     - "Add Workout"
│     └── WeekNav (prev/next week arrows)
│
├── BlockOverview (training mode only, secondary screen)
│     ├── PhaseTimeline (visual: base → build → peak → taper)
│     ├── WeekGrid (clickable weeks, current highlighted)
│     └── Stats (completion rate, miles logged)
│
├── GoalSetup (modal/flow)
│     ├── "Start Training Block" → race picker, date, generates plan
│     └── "Just Staying Fit" → sets maintenance mode
│
└── Settings
      ├── Profile (available days, experience level)
      └── Current goal management
```

---

## Components Being Replaced

| Current Component | Replacement | Reason |
|-------------------|-------------|--------|
| `WeekAheadView.jsx` (300+ lines) | `WeekView` + subcomponents | Too many responsibilities |
| `PlanManager/` (entire folder) | `BlockOverview` | Simpler mental model |
| `ChatInterface.jsx` | `GoalSetup` flow | Guided > chat-based |
| `MonthView.jsx` | Keep (optional alternate view) | Still useful |

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

- [ ] `TrainingBlock` model + Alembic migration
- [ ] Update `Workout` model (add `training_block_id`, `phase`, `actuals`)
- [ ] `/api/week` endpoint (new unified weekly view)
- [ ] `/api/training-block` CRUD endpoints
- [ ] Migration script: `WorkoutPlan` → `TrainingBlock`

### Phase 3: New Frontend Core
**Goal:** Replace WeekAheadView with new WeekView

- [ ] `WeekHeader` component (phase/mode context)
- [ ] `DayCard` component (single day with workouts)
- [ ] `WorkoutCard` updates (quick actions)
- [ ] `WeekView` assembly (compose header + days + actions)
- [ ] Week navigation (prev/next + scroll to past)

### Phase 4: Goal Setup Flow
**Goal:** Replace chat-based plan generation

- [ ] `GoalSetup` modal ("Start Training Block" vs "Stay Fit")
- [ ] Race setup flow (event, date, experience → LLM generates block)
- [ ] Phase visualization (show phases before confirming)
- [ ] Phase adjustment UI (edit lengths with friction modal)

### Phase 5: Polish & Multi-user
**Goal:** Production-ready

- [ ] `BlockOverview` screen (visual timeline)
- [ ] Regenerate with context ("I'm tired" → smarter output)
- [ ] Multi-user support (LOC-8: User model, auth, data isolation)
- [ ] Remove deprecated components

---

## What Gets Deprecated

After migration completes:

**Models:**
- `WorkoutPlan` → replaced by `TrainingBlock`

**Endpoints:**
- `POST /api/chat` → replaced by `POST /api/training-block`
- `GET /api/workout-plans` → replaced by `GET /api/training-block`
- `POST /api/workout-plans/:id/activate` → no longer needed (one block per user)

**Components:**
- `WeekAheadView.jsx`
- `ChatInterface.jsx`
- `PlanManager/` folder
- `PlanCard.jsx`, `PlanList.jsx`, `ActivePlanView.jsx`

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

- LOC-8: Create User Profiles and Beta Access System (Phase 5)
- LOC-20: Unable to edit when workout is rest (fix during Phase 3)
- LOC-22: Include additional workouts per day (already implemented, verify in Phase 3)
- LOC-18: Fix workout card display (address in Phase 3)
- LOC-17: Plan management usability (superseded by new architecture)
