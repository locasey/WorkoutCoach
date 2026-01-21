# Workout Coach MVP - Requirements & Architecture

## 1. Project Overview

A locally hosted web application that generates personalized workout plans through a chat interface and can import training data from Strava. The MVP focuses on workout plan generation and data import capabilities.

## 2. MVP Requirements

### 2.1 Functional Requirements

#### FR1: Workout Plan Generation
- **FR1.1**: User can input training goals via chat interface (e.g., "Create a 12-week half marathon training plan")
- **FR1.2**: System generates a structured workout plan using LLM
- **FR1.3**: User can export the generated workout plan to Excel format (.xlsx)
- **FR1.4**: Workout plan includes:
  - Weekly schedule
  - Workout types (e.g., long run, tempo, intervals, rest)
  - Duration/distance recommendations
  - Notes/instructions per workout

#### FR2: Strava Data Import
- **FR2.1**: User can authenticate with Strava API
- **FR2.2**: System can fetch user's activity data from Strava
- **FR2.3**: System displays imported activities (read-only for MVP)
- **FR2.4**: Data includes: date, activity type, distance, duration, pace, heart rate (if available)

### 2.2 Non-Functional Requirements

- **NFR1**: Application runs locally (localhost)
- **NFR2**: Mobile-first responsive web interface (optimized for one-handed training use)
- **NFR3**: High-glancability UI for workout tracking (large metrics, high contrast)
- **NFR4**: Fast response time for chat interactions (< 5 seconds)
- **NFR4**: Secure API key management for Strava and LLM services
- **NFR5**: Excel export should be properly formatted and readable

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────┐
│   Web Browser   │
│  (Frontend UI)  │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼─────────────────────────┐
│      Backend Server              │
│  ┌───────────────────────────┐  │
│  │   Chat/API Endpoints      │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │   LLM Service Client      │  │
│  │   (OpenAI/Anthropic/etc)  │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │   Strava API Client       │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │   Excel Generator         │  │
│  │   (openpyxl/xlsxwriter)   │  │
│  └───────────────────────────┘  │
└──────────────────────────────────┘
         │
         │
┌────────▼────────┐
│  External APIs  │
│  - LLM API      │
│  - Strava API   │
└─────────────────┘
```

### 3.2 Component Breakdown

#### Frontend
- **Chat Interface**: Interactive chat UI for workout plan requests
- **Data Import View**: Strava authentication and activity display
- **Export Controls**: Button to trigger Excel export

#### Backend
- **API Server**: RESTful endpoints for chat, data import, and export
- **LLM Integration**: Service to communicate with LLM API for workout generation
- **Strava Integration**: OAuth flow and data fetching from Strava API
- **Excel Generator**: Service to create formatted Excel files from workout plans
- **Data Models**: Structures for workout plans and activity data

## 4. Technology Stack Recommendations

### Frontend
- **Framework**: React or Vue.js (or vanilla JS for simplicity)
- **UI Library**: Tailwind CSS or Material-UI for quick styling
- **HTTP Client**: Axios or Fetch API

### Backend
- **Runtime**: Node.js (Express) or Python (Flask/FastAPI)
- **LLM Integration**: OpenAI API or Anthropic Claude API
- **Excel Generation**: 
  - Python: `openpyxl` or `xlsxwriter`
  - Node.js: `exceljs` or `xlsx`
- **Strava Integration**: `strava-api` library or direct REST calls

### Data Storage (MVP)
- **In-Memory**: Simple data structures (workout plans, imported activities)
- **Future**: SQLite or PostgreSQL for persistence

## 5. Data Flow

### 5.1 Workout Plan Generation Flow

```
User Input → Frontend → Backend API → LLM Service
                                    ↓
                            Structured Workout Plan
                                    ↓
                            Store in Memory
                                    ↓
                            Excel Export on Request
```

### 5.2 Strava Data Import Flow

```
User Clicks "Import from Strava" → OAuth Redirect → Strava Authorization
                                                          ↓
                                    Backend Receives Auth Code
                                                          ↓
                                    Exchange for Access Token
                                                          ↓
                                    Fetch Activities via Strava API
                                                          ↓
                                    Display Activities in UI
```

## 6. API Endpoints (Proposed)

### Workout Generation
- `POST /api/chat` - Send chat message, receive workout plan
- `GET /api/workout-plan` - Retrieve current workout plan
- `GET /api/export/excel` - Download workout plan as Excel

### Strava Integration
- `GET /api/strava/auth` - Initiate Strava OAuth
- `GET /api/strava/callback` - Handle OAuth callback
- `GET /api/strava/activities` - Fetch user activities
- `POST /api/strava/import` - Import selected activities

## 7. Data Models

### Workout Plan
```javascript
{
  id: string,
  goal: string,
  duration: number, // weeks
  createdAt: timestamp,
  workouts: [
    {
      week: number,
      day: number,
      type: string, // "long_run", "tempo", "intervals", "rest"
      distance: number, // km or miles
      duration: number, // minutes
      pace: string, // target pace
      notes: string
    }
  ]
}
```

### Activity (Strava)
```javascript
{
  id: string,
  name: string,
  type: string, // "Run", "Ride", etc.
  distance: number, // meters
  moving_time: number, // seconds
  elapsed_time: number, // seconds
  start_date: timestamp,
  average_speed: number, // m/s
  average_heartrate: number, // bpm (if available)
  strava_id: string
}
```

## 8. Security Considerations

- Store API keys in environment variables (`.env` file)
- Never expose API keys to frontend
- Use HTTPS for Strava OAuth (even in localhost with ngrok/tunnel if needed)
- Validate and sanitize user inputs
- Rate limiting for API calls (future)

## 9. MVP Implementation Phases

### Phase 1: Core Setup
- Set up project structure
- Configure development environment
- Set up basic frontend and backend

### Phase 2: Chat & Workout Generation
- Implement chat interface
- Integrate LLM API
- Parse and structure workout plan response
- Basic UI to display workout plan

### Phase 3: Excel Export
- Implement Excel generation
- Format workout plan data
- Add export button and download functionality

### Phase 4: Strava Integration
- Set up Strava OAuth flow
- Implement activity fetching
- Display imported activities
- Basic data visualization (table/list)

## 10. Future Enhancements (Post-MVP)

- **Training Evaluation**: Compare actual vs. planned workouts
- **Data Visualization**: Charts and graphs for training metrics
- **Coaching Feedback**: AI-generated insights and recommendations
- **Plan Refinement**: Learn from user feedback to improve plans
- **Database Persistence**: Store plans and activities
- **User Accounts**: Multi-user support
- **Advanced Analytics**: Training load, fitness trends, injury risk

## 11. Development Environment Setup

### Prerequisites
- Node.js/Python runtime
- npm/pip package manager
- Git
- API keys for:
  - LLM service (OpenAI/Anthropic)
  - Strava API (Client ID and Secret)

### Project Structure (Suggested)
```
workoutCoach/
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/
│   ├── src/
│   ├── .env.example
│   └── requirements.txt (or package.json)
├── ARCHITECTURE.md
└── README.md
```

## 12. Success Criteria for MVP

- ✅ User can request a workout plan via chat
- ✅ System generates a structured workout plan
- ✅ User can export plan to Excel
- ✅ User can authenticate with Strava
- ✅ System can fetch and display Strava activities
- ✅ Application runs locally without errors
- ✅ Basic UI is functional and responsive

