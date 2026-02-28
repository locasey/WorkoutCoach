# Changelog

## Unreleased

### Added
- **Tier-based model routing** — LLM model selected by user role at call time. `super_admin` gets frontier models (Gemini 2.5 Pro / Claude Opus 4.6 / GPT-4o), `beta_tester` stays on lite defaults.
- **Anthropic Claude support** — `_generate_with_anthropic()` added; `anthropic>=0.40.0` in requirements. Set `ANTHROPIC_API_KEY` to enable.
- **Multi-provider init** — All three providers (Gemini, OpenAI, Anthropic) initialize at startup if their API keys are present. No-op if key absent; only the primary provider must be configured.
- **`GET /api/llm/models`** — Returns full model catalog across all providers with `available: bool` per model based on caller's role. Response includes `active_model` and `primary_provider`.
- **`MODEL_TIERS`, `ALL_MODELS`, `MODEL_PROVIDER_MAP`** constants in `llm_service.py` — single source of truth for model catalog and tier assignments.

### Changed
- `LLMService._dispatch()` now routes each LLM call to the correct provider API based on model ID, not the global `LLM_PROVIDER` env var. Provider env var still sets the default tier model.
- `generate_periodized_workouts()` and `generate_workout_plan()` accept `user_role=None`; defaults to `beta_tester` tier (backward-compatible).
- `PeriodizedWorkoutService.generate_workouts_for_block()` and `TrainingBlockService.regenerate_week()` accept `user_role=None` and thread it to LLM calls.

---

## Key Milestones

### Multi-User Auth & Profiles (Phase 6)
- Google OAuth login with invite-code gating for beta access
- Full data isolation between users (7 service methods + 10 endpoints secured)
- User preferences: available training days, experience level, distance unit (mi/km)
- Profile page with account info and training settings

### Weekly Regeneration & Block Overview (Phase 5)
- `POST /api/week/regenerate` — snapshots old workouts, LLM generates new ones respecting phase
- Block overview with phase timeline, completion stats, progress tracking
- Coach tab is state-aware: no block shows GoalSetup, active block shows week view

### Goal Setup Flow (Phase 4)
- 3-step wizard: mode select, race details, phase preview with adjustable timeline
- Phase-by-phase LLM workout generation (base, build, peak, taper)
- Start date selection (today, next Monday, or custom)

### WeekView Components (Phase 3)
- Composable week display: WeekHeader, DayCard, WeekNav, WeekActions
- Mobile-first: scrollable day pills + hero card below 768px, 7-column grid on desktop
- React Query for all data fetching

### Training Block Architecture (Phase 2)
- `TrainingBlock` model with periodization phases (Lydiard-style)
- Unified `/api/week` endpoint for both training and maintenance modes
- Multiple workouts per day (AM/PM slots)

### Foundation (Phase 1)
- Design tokens, centralized API routes, React Query setup
- Flask REST API with service-oriented architecture
- LLM abstraction supporting Gemini and OpenAI
- Production deployment: AWS Lightsail + S3 + CloudFront
