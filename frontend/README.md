# Frontend - Workout Coach UI

React-based frontend for the Workout Coach application.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

## Running

```bash
npm run dev
```

Frontend will start on `http://localhost:3000`

## Building for Production

```bash
npm run build
```

Built files will be in the `dist/` directory.

## Project Structure

```
src/
  ├── App.jsx           # Main app component
  ├── App.css           # App styles
  ├── main.jsx          # Entry point
  ├── index.css         # Global styles
  └── components/
      ├── ChatInterface.jsx    # Workout plan generation UI
      ├── ChatInterface.css
      ├── StravaImport.jsx     # Strava data import UI
      └── StravaImport.css
```

