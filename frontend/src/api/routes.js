/**
 * API Routes
 *
 * Centralized API endpoint definitions for the Workout Coach application.
 * This file serves as the single source of truth for all backend API paths.
 *
 * Usage:
 *   import { API_ROUTES } from '@/api/routes'
 *   axios.get(API_ROUTES.WORKOUTS.WEEK)
 *
 * Benefits:
 *   - Easy to refactor endpoints
 *   - IDE autocomplete for route names
 *   - Clear documentation of available endpoints
 *
 * @see docs/ARCHITECTURE_ROADMAP.md - Target API Structure
 */

/**
 * Current API Routes (Legacy)
 * These are the existing endpoints that work with WorkoutPlan model.
 * Will be deprecated in favor of Training Block endpoints.
 */
export const API_ROUTES = {
  /* ==========================================================================
   * AUTHENTICATION
   * ========================================================================== */
  AUTH: {
    CHECK: '/api/auth/check',
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
  },

  /* ==========================================================================
   * CHAT / PLAN GENERATION (Deprecated - replaced by GoalSetup + Training Block)
   * ========================================================================== */
  CHAT: {
    /** POST - Generate new workout plan from chat message (Deprecated) */
    GENERATE: '/api/chat',
  },

  /* ==========================================================================
   * WORKOUT PLANS (Deprecated - replaced by Training Block)
   * ========================================================================== */
  WORKOUT_PLANS: {
    /** GET - List all plans with metadata */
    LIST: '/api/workout-plans',
    /** GET - Get currently active plan */
    ACTIVE: '/api/workout-plans/active',
    /** GET/PATCH/DELETE - Single plan operations */
    BY_ID: (id) => `/api/workout-plans/${id}`,
    /** POST - Set plan as active */
    ACTIVATE: (id) => `/api/workout-plans/${id}/activate`,
    /** GET - Export plan as Excel file */
    EXPORT_EXCEL: (id) => `/api/export/excel/${id}`,
  },

  /* ==========================================================================
   * WORKOUTS
   * ========================================================================== */
  WORKOUTS: {
    /** GET - Current week's workouts */
    WEEK: '/api/workouts/week',
    /** GET - Week by offset (0=current, -1=last, +1=next) */
    WEEK_OFFSET: (offset) => `/api/workouts/week/${offset}`,
    /** GET - Month's workouts */
    MONTH: (year, month) => `/api/workouts/month/${year}/${month}`,
    /** GET - Week progress summary */
    PROGRESS: '/api/workouts/progress',
    /** GET/PUT/DELETE - Single workout operations */
    BY_ID: (id) => `/api/workouts/${id}`,
    /** PUT - Toggle workout completion */
    COMPLETE: (id) => `/api/workouts/${id}/complete`,
    /** POST - Add workout to a day */
    ADD_TO_DAY: '/api/workouts/day',
    /** GET - All workouts for a specific date */
    BY_DATE: (date) => `/api/workouts/day/${date}`,
  },

  /* ==========================================================================
   * STRAVA INTEGRATION (Disabled by default - LOC-23)
   * ========================================================================== */
  STRAVA: {
    /** GET - OAuth authorization URL */
    AUTH: '/api/strava/auth',
    /** GET - OAuth callback */
    CALLBACK: '/api/strava/callback',
    /** GET - Fetch activities */
    ACTIVITIES: '/api/strava/activities',
    /** GET - Validate connection */
    VALIDATE: '/api/strava/validate',
  },

  /* ==========================================================================
   * TRAINING BLOCK (New Architecture - Phase 2)
   *
   * These endpoints will be implemented in Phase 2.
   * Uncomment and use when backend is ready.
   * ========================================================================== */
  TRAINING_BLOCK: {
    /** GET - Current block (or null if maintenance mode) */
    CURRENT: '/api/training-block',
    /** POST - Create new block, LLM generates periodized plan */
    CREATE: '/api/training-block',
    /** PUT - Update block (reschedule race, adjust phases) */
    UPDATE: (id) => `/api/training-block/${id}`,
    /** PUT - Adjust phase lengths (with friction confirmation) */
    UPDATE_PHASES: (id) => `/api/training-block/${id}/phases`,
    /** DELETE - End block early (with friction confirmation) */
    DELETE: (id) => `/api/training-block/${id}`,
    /** GET - Full plan visualization for overview screen */
    OVERVIEW: (id) => `/api/training-block/${id}/overview`,
    /** POST - Generate periodized workouts for a block */
    GENERATE_WORKOUTS: (id) => `/api/training-block/${id}/generate-workouts`,
  },

  /* ==========================================================================
   * UNIFIED WEEK VIEW (New Architecture - Phase 2)
   *
   * These endpoints will be implemented in Phase 2.
   * Works for both Training Block and Maintenance modes.
   * ========================================================================== */
  WEEK: {
    /** GET - Current week context + workouts (supports ?offset= query param) */
    CURRENT: '/api/week',
    /** POST - Regenerate week with optional context */
    REGENERATE: '/api/week/regenerate',
  },
}

/**
 * Helper to build URL with query parameters
 *
 * @param {string} baseUrl - The base endpoint URL
 * @param {Object} params - Query parameters as key-value pairs
 * @returns {string} URL with query string appended
 *
 * @example
 *   buildUrl(API_ROUTES.WEEK.CURRENT, { offset: -1 })
 *   // => '/api/week?offset=-1'
 */
export const buildUrl = (baseUrl, params = {}) => {
  const searchParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.append(key, String(value))
    }
  })

  const queryString = searchParams.toString()
  return queryString ? `${baseUrl}?${queryString}` : baseUrl
}

/**
 * HTTP method constants for clarity
 */
export const HTTP_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  PATCH: 'PATCH',
  DELETE: 'DELETE',
}

export default API_ROUTES
