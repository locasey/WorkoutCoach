/**
 * React Query Client Configuration
 *
 * Configures TanStack Query (React Query v5) for the Workout Coach application.
 * Provides sensible defaults for caching, refetching, and error handling.
 *
 * Usage:
 *   Wrap your App component with QueryClientProvider in main.jsx
 *
 * @see https://tanstack.com/query/latest/docs/framework/react/overview
 * @see docs/ARCHITECTURE_ROADMAP.md - Phase 1: React Query setup
 */

import { QueryClient } from '@tanstack/react-query'

/**
 * Default query options for all queries
 *
 * These can be overridden per-query using the options parameter.
 */
const defaultQueryOptions = {
  queries: {
    /**
     * How long data is considered fresh (won't refetch).
     * 30 seconds for workout data - strikes balance between freshness and API calls.
     */
    staleTime: 30 * 1000, // 30 seconds

    /**
     * How long to keep inactive query data in cache.
     * 5 minutes allows quick navigation without refetching.
     */
    gcTime: 5 * 60 * 1000, // 5 minutes (formerly cacheTime)

    /**
     * Retry failed queries up to 2 times with exponential backoff.
     * Helps recover from transient network issues.
     */
    retry: 2,

    /**
     * Refetch data when window regains focus.
     * Keeps data fresh when user returns to the app.
     */
    refetchOnWindowFocus: true,

    /**
     * Don't refetch on component mount if data is still fresh.
     * Reduces unnecessary API calls.
     */
    refetchOnMount: true,

    /**
     * Refetch when network connection is restored.
     * Ensures data is current after offline period.
     */
    refetchOnReconnect: true,
  },
  mutations: {
    /**
     * Don't retry mutations by default.
     * Mutations should be explicit and not automatically retried.
     */
    retry: 0,
  },
}

/**
 * Create and configure the QueryClient instance
 *
 * This client should be used throughout the application via QueryClientProvider.
 */
export const queryClient = new QueryClient({
  defaultOptions: defaultQueryOptions,
})

/**
 * Query key factories
 *
 * Standardized query keys for cache management and invalidation.
 * Using factories ensures consistent keys across the app.
 *
 * @example
 *   useQuery({ queryKey: queryKeys.workouts.week(0), ... })
 *   queryClient.invalidateQueries({ queryKey: queryKeys.workouts.all })
 */
export const queryKeys = {
  /**
   * Workout-related queries
   */
  workouts: {
    /** Base key for all workout queries */
    all: ['workouts'],

    /** Current week's workouts */
    week: (offset = 0) => ['workouts', 'week', offset],

    /** Specific month's workouts */
    month: (year, month) => ['workouts', 'month', year, month],

    /** Single workout by ID */
    detail: (id) => ['workouts', 'detail', id],

    /** Workouts for a specific date */
    byDate: (date) => ['workouts', 'date', date],

    /** Progress summary */
    progress: (weekOffset = 0) => ['workouts', 'progress', weekOffset],
  },

  /**
   * Workout plan queries (Legacy - will be deprecated)
   */
  plans: {
    /** Base key for all plan queries */
    all: ['plans'],

    /** Active plan */
    active: ['plans', 'active'],

    /** Single plan by ID */
    detail: (id) => ['plans', 'detail', id],
  },

  /**
   * Training block queries (New Architecture - Phase 2)
   */
  trainingBlock: {
    /** Base key for all training block queries */
    all: ['trainingBlock'],

    /** Current active block */
    current: ['trainingBlock', 'current'],

    /** Block overview (phases, stats) */
    overview: ['trainingBlock', 'overview'],
  },

  /**
   * Unified week view (New Architecture - Phase 2)
   */
  week: {
    /** Base key for week queries */
    all: ['week'],

    /** Week by offset (supports both modes) */
    byOffset: (offset = 0) => ['week', offset],
  },

  /**
   * User/auth related queries
   */
  auth: {
    /** Auth status check */
    status: ['auth', 'status'],
  },

  /**
   * User profile and preferences
   */
  user: {
    profile: ['user', 'profile'],
  },
}

/**
 * Invalidation helpers
 *
 * Common patterns for invalidating related queries after mutations.
 */
export const invalidateHelpers = {
  /**
   * Invalidate all workout-related queries
   * Use after completing a workout or modifying the week.
   */
  allWorkouts: () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.workouts.all })
  },

  /**
   * Invalidate current week data
   * Use after workout completion or day changes.
   */
  currentWeek: () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.workouts.week(0) })
    queryClient.invalidateQueries({ queryKey: queryKeys.workouts.progress(0) })
  },

  /**
   * Invalidate all plan-related queries
   * Use after creating, activating, or deleting plans.
   */
  allPlans: () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.plans.all })
  },
}

export default queryClient
