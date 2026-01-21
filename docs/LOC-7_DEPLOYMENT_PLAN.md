# LOC-7: Deploy Application to Cloud Server

**Overall Progress:** `0%`

## TLDR

Deploy the Workout Coach application to AWS Lightsail so it's accessible at `workoutcoach.liamocasey.com`. Includes containerizing the backend, building the frontend as static files, adding simple authentication to keep it private, and configuring DNS/SSL.

## Critical Decisions

- **Platform**: AWS Lightsail - 3 months free, simple container hosting, good AWS exposure
- **Domain**: `workoutcoach.liamocasey.com` - subdomain (free), easier SSL than path-based
- **Database**: Neon PostgreSQL - already configured, no changes needed
- **Architecture**: Separate services - backend container + frontend static files
- **Authentication**: Simple env credentials - username/password in environment variables
- **CORS**: Restricted to production domain in production only
- **Strava OAuth**: Keep localhost for now - LOC-10 handles production switch later

## Tasks

- [ ] **Step 1: Add Simple Authentication to Backend**
  - [ ] Create auth middleware that checks for valid session
  - [ ] Add login endpoint (`POST /api/auth/login`)
  - [ ] Add logout endpoint (`POST /api/auth/logout`)
  - [ ] Add auth check endpoint (`GET /api/auth/check`)
  - [ ] Protect all existing API routes (except health check)
  - [ ] Add `AUTH_USERNAME` and `AUTH_PASSWORD` to `env.template`

- [ ] **Step 2: Add Login UI to Frontend**
  - [ ] Create `LoginPage.jsx` component with username/password form
  - [ ] Add auth state management in `App.jsx`
  - [ ] Redirect to login if not authenticated
  - [ ] Store session token in localStorage
  - [ ] Add logout button to main UI

- [ ] **Step 3: Make URLs Environment-Driven**
  - [ ] Add `FRONTEND_URL` env var for OAuth callback redirect
  - [ ] Update `backend/app.py` line 577 to use `FRONTEND_URL`
  - [ ] Add `CORS_ORIGINS` env var for production CORS
  - [ ] Update CORS config to use `CORS_ORIGINS` in production
  - [ ] Add `VITE_API_URL` for frontend production builds
  - [ ] Update frontend to use `VITE_API_URL` when set

- [ ] **Step 4: Create Backend Dockerfile**
  - [ ] Create `backend/Dockerfile` with Python 3.11 base
  - [ ] Install dependencies from `requirements.txt`
  - [ ] Use gunicorn for production server
  - [ ] Add `gunicorn` to `requirements.txt`
  - [ ] Expose port 5000

- [ ] **Step 5: Create Frontend Production Build**
  - [ ] Update `vite.config.js` to handle production API URL
  - [ ] Test `npm run build` creates working static files
  - [ ] Document build command for deployment

- [ ] **Step 6: Create Production Environment Template**
  - [ ] Create `backend/env.production.template` with all required vars
  - [ ] Document each variable's purpose
  - [ ] Include placeholder values

- [ ] **Step 7: Set Up AWS Lightsail**
  - [ ] Create AWS account (if needed)
  - [ ] Create Lightsail container service
  - [ ] Push backend Docker image to Lightsail
  - [ ] Configure environment variables in Lightsail
  - [ ] Deploy backend container
  - [ ] Verify backend health endpoint works

- [ ] **Step 8: Deploy Frontend Static Files**
  - [ ] Build frontend with production API URL
  - [ ] Create Lightsail static site (or use S3 + CloudFront)
  - [ ] Upload built files
  - [ ] Verify frontend loads

- [ ] **Step 9: Configure DNS & SSL**
  - [ ] Add CNAME record for `workoutcoach.liamocasey.com` pointing to Lightsail
  - [ ] Enable SSL certificate in Lightsail
  - [ ] Verify HTTPS works
  - [ ] Test full authentication flow

- [ ] **Step 10: Run Database Migrations**
  - [ ] Verify Neon DATABASE_URL is set in Lightsail
  - [ ] Run Alembic migrations against production database
  - [ ] Verify tables exist and app connects

- [ ] **Step 11: Final Testing**
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
- Frontend needs to be rebuilt whenever `VITE_API_URL` changes
- Database migrations should be run before first deployment

