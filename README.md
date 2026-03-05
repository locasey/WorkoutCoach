# Workout Coach

A personalized training plan generator that uses LLMs to create periodized running programs adapted to your goals, schedule, and experience level.

## The Problem

Most runners either follow generic training plans that ignore their schedule and fitness level, or pay for a human coach. I wanted something in between — a tool that generates structured, periodized weekly plans (base, build, peak, taper) and lets you adjust on the fly without losing the overall structure. It's an ongoing project — I'm actively iterating on prompt engineering and plan quality to get workouts that feel like they came from a real coach (not an LLM).

## How It Works

```
User sets goal        →  App calculates phase structure  →  LLM generates workouts
(e.g. "Half marathon,       (Lydiard-style periodization)     per phase, per week
 May 10, intermediate")

Weekly loop:
  See this week's plan  →  Complete workouts  →  Regenerate if needed  →  Next week
```

The app operates in two modes:
- **Training Block** — You set a race goal and target date. The app builds a multi-week periodized plan with phase-specific workouts (easy runs, tempos, intervals, long runs, rest days).
- **Maintenance** — No active goal. The app suggests weekly workouts to stay fit without rigid structure.

## Tech Stack

- **Frontend:** React (Vite), mobile-responsive with tab navigation
- **Backend:** Flask, SQLAlchemy ORM, PostgreSQL (Neon)
- **LLM Integration:** Google Gemini (default) or OpenAI — structured prompting for periodized plan generation
- **Auth:** Google OAuth with invite-code gating for beta access
- **Deployment:** AWS Lightsail (Docker), CloudFront CDN, S3 static hosting
- **Migrations:** Alembic for schema versioning

## Key Features

- **Periodized plan generation** — LLM creates phase-appropriate workouts (base, build, peak, taper) based on race distance, target date, and experience level
- **Weekly regeneration** — Regenerate any week's workouts with optional context ("I was sick this week") while preserving phase structure. Old workouts are snapshot-archived.
- **Two-mode coaching** — Structured training blocks for race prep, flexible maintenance mode between goals
- **Multi-user with beta gating** — Google OAuth login, invite codes for controlled access, full data isolation between users
- **Mobile-first week view** — Scrollable day pills on mobile, 7-column grid on desktop, workout completion tracking

## Project Structure

```
backend/
  app.py                 # Flask API (REST endpoints)
  models/                # SQLAlchemy models (User, TrainingBlock, Workout, etc.)
  services/              # Business logic layer
    llm_service.py       #   LLM abstraction (Gemini/OpenAI)
    training_block_service.py  #   Block CRUD, week context, regeneration
    periodized_workout_service.py  #   Phase-by-phase LLM generation
    auth_service.py      #   Google OAuth + session management
  alembic/               # Database migrations
frontend/
  src/
    components/
      WeekView/          # Weekly training display (header, day cards, nav)
      GoalSetup/         # 3-step wizard for creating training blocks
      BlockOverview/     # Plan timeline, phase progress, stats
    utils/
      workoutMapper.js   # Workout type mapping, unit conversion
      phaseCalculator.js # Phase distribution logic
      dateUtils.js       # Timezone-safe date parsing
```

## Setup

```bash
# Clone
git clone https://github.com/locasey/workoutCoach.git && cd workoutCoach

# Backend
cd backend
python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp env.template .env  # Add your Gemini API key, database URL, and Google OAuth credentials
alembic upgrade head
python app.py  # http://localhost:5000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev  # http://localhost:3000
```

Requires: Python 3.8+, Node.js 16+, PostgreSQL database, Google Cloud OAuth credentials, Gemini or OpenAI API key.

## What I'd Build Next

- **RAG-enhanced workout quality** — Supplement LLM prompts with retrieval from training science literature (Daniels, Pfitzinger, etc.) to ground workout prescriptions in established methodology rather than relying solely on the model's training data.
- **Strava integration** — OAuth flow is built but disabled. Would pull actual training data to compare planned vs. completed and inform regeneration.
- **Smarter regeneration** — Feed completion history and Strava data back into the LLM prompt so the coach adapts to how training is actually going, not just the plan.
- **Analytics dashboard** — Weekly mileage trends, phase completion rates, adherence tracking. The data model supports it; the UI doesn't exist yet.

---

*Built by Liam O'Casey. Development was AI-assisted (Claude, Cursor) — I drove product direction, architecture decisions, and UX design.*
