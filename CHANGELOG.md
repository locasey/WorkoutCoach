# Changelog

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
