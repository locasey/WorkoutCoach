# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
- Session tokens use `secrets.token_urlsafe(32)` for cryptographic randomness
- Constant-time credential comparison via `secrets.compare_digest`
- Auth cookies: `httponly=True`, `secure=True` (production), `samesite=Lax`
- Non-root user in backend Docker container

### Fixed
- **Critical**: Fixed blank screen bug caused by undefined `swipeHandlers` in WeekAheadView - `useSwipeable` hook was imported but never called.
- Improved mobile responsiveness across all main views.
- Optimized touch targets for accessibility and ease of use on small screens.
- Removed unnecessary container and header borders in Week view for cleaner UI.

