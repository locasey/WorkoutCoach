# Backend - Workout Coach API

Flask-based REST API for workout plan generation and Strava integration.

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file (copy from `env.template`):
   ```bash
   copy env.template .env  # Windows
   # or
   cp env.template .env    # macOS/Linux
   ```

4. Add your API keys to `.env`:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `STRAVA_CLIENT_ID`: Your Strava app Client ID
   - `STRAVA_CLIENT_SECRET`: Your Strava app Client Secret

## Running

```bash
python app.py
```

Server will start on `http://localhost:5000`

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/chat` - Generate workout plan
- `GET /api/workout-plan/<plan_id>` - Get workout plan
- `GET /api/export/excel/<plan_id>` - Export to Excel
- `GET /api/strava/auth` - Initiate Strava OAuth
- `GET /api/strava/callback` - Strava OAuth callback
- `GET /api/strava/activities` - Fetch Strava activities

