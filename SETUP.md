# Setup Guide

This guide will walk you through setting up the Workout Coach MVP on your local machine.

## Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] Node.js 16 or higher installed
- [ ] OpenAI API key
- [ ] Strava API credentials (Client ID and Secret)

## Step-by-Step Setup

### Step 1: Verify Prerequisites

**Check Python version:**
```bash
python --version
# Should show Python 3.8 or higher
```

**Check Node.js version:**
```bash
node --version
# Should show v16 or higher
```

### Step 2: Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   ```bash
   # Copy the template file
   copy env.template .env  # Windows
   # or
   cp env.template .env    # macOS/Linux
   ```

6. **Edit `.env` file** and add your API keys:
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   STRAVA_CLIENT_ID=your_client_id
   STRAVA_CLIENT_SECRET=your_client_secret
   STRAVA_REDIRECT_URI=http://localhost:5000/api/strava/callback
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=change-this-to-a-random-string
   ```

### Step 3: Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

### Step 4: Getting API Keys

#### OpenAI API Key

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new secret key
5. Copy the key and add it to your `.env` file

#### Strava API Credentials

1. Go to https://www.strava.com/settings/api
2. Click "Create App" or "My API Application"
3. Fill in the application details:
   - **Application Name**: Workout Coach (or any name)
   - **Category**: Website
   - **Website**: http://localhost:3000
   - **Authorization Callback Domain**: localhost
4. Click "Create"
5. Copy the **Client ID** and **Client Secret**
6. Add them to your `.env` file

### Step 5: Run the Application

You'll need **two terminal windows** running simultaneously:

**Terminal 1 - Backend Server:**
```bash
cd backend
# Make sure virtual environment is activated
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

**Terminal 2 - Frontend Development Server:**
```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

### Step 6: Access the Application

Open your web browser and navigate to:
```
http://localhost:3000
```

You should see the Workout Coach interface!

## Testing the Application

### Test Workout Plan Generation

1. Click on the "💬 Generate Workout Plan" tab
2. Type a message like: "Create a 12-week half marathon training plan"
3. Wait for the AI to generate your plan
4. Review the plan preview
5. Click "📥 Export to Excel" to download the plan

### Test Strava Integration

1. Click on the "📊 Strava Import" tab
2. Click "🔗 Connect to Strava"
3. Authorize the application in Strava
4. You'll be redirected back to the app
5. Click "📥 Fetch Activities" to import your activities

## Troubleshooting

### Backend Issues

**Port 5000 already in use:**
- Change the port in `backend/app.py`: `app.run(debug=True, host='0.0.0.0', port=5001)`
- Update `frontend/vite.config.js` proxy target to match

**Module not found errors:**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**OpenAI API errors:**
- Verify your API key is correct in `.env`
- Check your OpenAI account has credits

### Frontend Issues

**Port 3000 already in use:**
- Vite will automatically use the next available port
- Check the terminal output for the actual port

**Cannot connect to backend:**
- Verify backend is running on port 5000
- Check `vite.config.js` proxy configuration

**npm install fails:**
- Try deleting `node_modules` and `package-lock.json`
- Run `npm install` again

### Strava Issues

**OAuth callback fails:**
- Verify `STRAVA_REDIRECT_URI` in `.env` matches exactly: `http://localhost:5000/api/strava/callback`
- Check Strava app settings have `localhost` as callback domain

**No activities showing:**
- Make sure you've authorized the app
- Try clicking "Fetch Activities" again
- Check browser console for errors

## Next Steps

Once everything is working:

1. Try generating different types of workout plans
2. Import your Strava activities
3. Export plans to Excel and review the formatting
4. Check out the [ARCHITECTURE.md](./ARCHITECTURE.md) for future enhancements

## Need Help?

- Check the [ARCHITECTURE.md](./ARCHITECTURE.md) for system design details
- Review error messages in browser console (F12) and terminal output
- Ensure all API keys are correctly set in `.env` file

