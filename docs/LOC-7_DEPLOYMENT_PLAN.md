# LOC-7: Deploy Application to Cloud Server

**Overall Progress:** `95%`

## TLDR

Deploy the Workout Coach application to AWS Lightsail so it's accessible at `workoutcoach.liamocasey.com`. Includes containerizing the backend, building the frontend as static files, adding simple authentication to keep it private, and configuring DNS/SSL.

## Critical Decisions

- **Platform**: AWS Lightsail - 3 months free, simple container hosting, good AWS exposure
- **Domain**: `workoutcoach.liamocasey.com` - subdomain (free), easier SSL than path-based
- **Database**: Neon PostgreSQL - already configured, no changes needed
- **Architecture**: Separate services - backend container + frontend static files (S3)
- **Authentication**: Simple env credentials - username/password in environment variables
- **CORS**: Restricted to production domain in production only
- **Strava OAuth**: Keep localhost for now - LOC-10 handles production switch later
- **CI/CD**: GitHub Actions - builds Docker remotely (no local Docker needed)

## Tasks

- [x] **Step 1: Add Simple Authentication to Backend** ✅
  - [x] Create auth middleware that checks for valid session
  - [x] Add login endpoint (`POST /api/auth/login`)
  - [x] Add logout endpoint (`POST /api/auth/logout`)
  - [x] Add auth check endpoint (`GET /api/auth/check`)
  - [x] Protect all existing API routes (except health check)
  - [x] Add `AUTH_USERNAME` and `AUTH_PASSWORD` to `env.template`

- [x] **Step 2: Add Login UI to Frontend** ✅
  - [x] Create `LoginPage.jsx` component with username/password form
  - [x] Add auth state management in `App.jsx`
  - [x] Redirect to login if not authenticated
  - [x] Store session token in localStorage
  - [x] Add logout button to main UI

- [x] **Step 3: Make URLs Environment-Driven** ✅
  - [x] Add `FRONTEND_URL` env var for OAuth callback redirect
  - [x] Update `backend/app.py` line 577 to use `FRONTEND_URL`
  - [x] Add `CORS_ORIGINS` env var for production CORS
  - [x] Update CORS config to use `CORS_ORIGINS` in production
  - [x] Add `VITE_API_URL` for frontend production builds
  - [x] Update frontend to use `VITE_API_URL` when set

- [x] **Step 4: Create Backend Dockerfile** ✅
  - [x] Create `backend/Dockerfile` with Python 3.11 base
  - [x] Install dependencies from `requirements.txt`
  - [x] Use gunicorn for production server
  - [x] Add `gunicorn` to `requirements.txt`
  - [x] Expose port 5000

- [x] **Step 5: Create Frontend Production Build** ✅
  - [x] Update `vite.config.js` to handle production API URL
  - [x] Create Frontend Dockerfile with nginx
  - [x] Document build command for deployment

- [x] **Step 6: Create Production Environment Template** ✅
  - [x] Create `backend/env.production.template` with all required vars
  - [x] Document each variable's purpose
  - [x] Include placeholder values
  - [x] Create `docker-compose.production.yml` for local testing

- [x] **Step 7: Create GitHub Actions Workflow** ✅
  - [x] Create `.github/workflows/deploy.yml`
  - [x] Configure backend build and push to Lightsail
  - [x] Configure frontend build and deploy to S3
  - [x] Add automatic deployment on push to main

- [x] **Step 8: Set Up AWS Infrastructure** ✅
  - [x] Install and configure AWS CLI locally
  - [x] Create IAM user with Lightsail + S3 permissions
  - [x] Create Lightsail container service
  - [x] Create S3 bucket for frontend

- [x] **Step 9: Configure GitHub Secrets** ✅
  - [x] Add AWS credentials to GitHub secrets
  - [x] Add all environment variables as secrets
  - [x] Push to main to trigger first deployment

- [x] **Step 10: Configure DNS & SSL** ✅
  - [x] Request ACM certificate for `workoutcoach.liamocasey.com` (us-east-1)
  - [x] Add DNS validation CNAME at GoDaddy
  - [x] Create CloudFront distribution with S3 website origin
  - [x] Configure alternate domain name and SSL certificate
  - [x] Add CNAME record `workoutcoach` → CloudFront distribution
  - [x] Add `CLOUDFRONT_DISTRIBUTION_ID` to GitHub secrets

- [x] **Step 11: Run Database Migrations** ✅
  - [x] Add migration job to GitHub Actions workflow (runs before deployment)
  - [x] Create manual migration script (`backend/scripts/run_migrations.py`)
  - [x] Migrations auto-run on next push to main
  - [x] Tables verified: `workout_plans`, `workouts`, `strava_sessions`, `strava_activities`, `auth_sessions`

- [ ] **Step 12: Final Testing** 📋 [See CLI Guide](LOC-7_STEP7_CLI_GUIDE.md#step-13-final-testing)
  - [ ] Test login from desktop browser
  - [ ] Test login from mobile phone
  - [ ] Test workout plan generation
  - [ ] Test all main features work
  - [ ] Verify unauthenticated access is blocked

## Out of Scope (Separate Tickets)

- **LOC-10**: Configure Strava OAuth for production domain
- **LOC-11**: Add Sentry error monitoring

## Environment Variables (Production)

```env
# Database
DATABASE_URL=<neon-connection-string>

# Flask
SECRET_KEY=<secure-random-32-char-key>
FLASK_ENV=production

# Authentication
AUTH_USERNAME=<your-username>
AUTH_PASSWORD=<your-password>

# LLM
LLM_PROVIDER=gemini
GEMINI_API_KEY=<your-key>

# Strava (keep localhost for now)
STRAVA_CLIENT_ID=<your-id>
STRAVA_CLIENT_SECRET=<your-secret>
STRAVA_REDIRECT_URI=http://localhost:5000/api/strava/callback

# Production URLs
FRONTEND_URL=https://workoutcoach.liamocasey.com
CORS_ORIGINS=https://workoutcoach.liamocasey.com

# App Config
MAX_WORKOUT_PLANS=5
```

## Notes

- Strava integration will only work locally until LOC-10 is completed
- Frontend is rebuilt automatically on each push to main
- **Database migrations run automatically** - CI/CD runs Alembic before deployment
- **No local Docker required** - GitHub Actions builds images remotely
- **Manual migrations**: Run `python scripts/run_migrations.py` in `backend/` directory
- **CLI Guide**: Full step-by-step AWS commands in [LOC-7_STEP7_CLI_GUIDE.md](LOC-7_STEP7_CLI_GUIDE.md)
- **GitHub Workflow**: [.github/workflows/deploy.yml](../.github/workflows/deploy.yml)

