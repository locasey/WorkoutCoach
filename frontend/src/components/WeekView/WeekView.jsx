/**
 * WeekView Component (Shell)
 *
 * New unified weekly view component that will replace WeekAheadView.
 * Supports both Training Block mode and Maintenance mode.
 *
 * Architecture:
 *   WeekView (this component)
 *   ├── WeekHeader - Shows phase/mode context
 *   ├── DayCards - 7 day cards with workouts
 *   │   └── WorkoutCard - Individual workout display
 *   ├── WeekActions - Regenerate, Add Workout buttons
 *   └── WeekNav - Previous/Next week navigation
 *
 * This is a shell component for Phase 1 foundation.
 * Full implementation comes in Phase 3.
 *
 * @see docs/ARCHITECTURE_ROADMAP.md - Target Frontend Architecture
 */

import React from 'react'
import { Calendar, ChevronLeft, ChevronRight } from 'lucide-react'
import './WeekView.css'

/**
 * WeekView - Main weekly training view
 *
 * Props (to be implemented in Phase 3):
 * @param {number} weekOffset - Week offset from current (0 = this week)
 * @param {function} onWeekChange - Callback when week changes
 *
 * Data fetching will use React Query in Phase 3:
 *   const { data, isLoading } = useQuery({
 *     queryKey: queryKeys.week.byOffset(weekOffset),
 *     queryFn: () => fetchWeekData(weekOffset)
 *   })
 */
export function WeekView({ weekOffset = 0, onWeekChange }) {
  /* =========================================================================
   * PLACEHOLDER STATE
   *
   * These will be replaced with React Query hooks in Phase 3:
   *   const { data: weekData } = useQuery(...)
   * ========================================================================= */

  // Mock data structure matching target API response shape
  const weekData = {
    mode: 'training', // 'training' | 'maintenance'
    week_number: 8,
    phase: 'build',
    phase_focus: 'Tempo & threshold work',
    weeks_until_race: 8,
    event_name: 'Boston Marathon',
    workouts: [],
  }

  const isTrainingMode = weekData.mode === 'training'

  /* =========================================================================
   * RENDER
   * ========================================================================= */

  return (
    <div className="week-view">
      {/* WEEK HEADER - Phase/mode context */}
      <header className="week-view__header">
        <div className="week-view__header-content">
          {isTrainingMode ? (
            <>
              <h1 className="week-view__title">
                Week {weekData.week_number} · {weekData.phase} Phase
              </h1>
              <p className="week-view__subtitle">
                {weekData.weeks_until_race} weeks to {weekData.event_name}
              </p>
              <span className="week-view__phase-focus">{weekData.phase_focus}</span>
            </>
          ) : (
            <>
              <h1 className="week-view__title">This Week</h1>
              <p className="week-view__subtitle">Staying fit, no specific goal</p>
            </>
          )}
        </div>
      </header>

      {/* WEEK NAVIGATION */}
      <nav className="week-view__nav" aria-label="Week navigation">
        <button
          className="week-view__nav-button"
          onClick={() => onWeekChange?.(weekOffset - 1)}
          aria-label="Previous week"
        >
          <ChevronLeft className="w-5 h-5" />
          <span>Previous</span>
        </button>

        <span className="week-view__nav-current">
          <Calendar className="w-4 h-4" />
          <span>Current Week</span>
        </span>

        <button
          className="week-view__nav-button"
          onClick={() => onWeekChange?.(weekOffset + 1)}
          aria-label="Next week"
        >
          <span>Next</span>
          <ChevronRight className="w-5 h-5" />
        </button>
      </nav>

      {/* DAY CARDS GRID - Placeholder for Phase 3 */}
      <section className="week-view__days" aria-label="Weekly workouts">
        <div className="week-view__placeholder">
          <Calendar className="w-12 h-12" />
          <h2>WeekView Shell</h2>
          <p>
            This component is a Phase 1 foundation shell.
            <br />
            Day cards and workout display will be implemented in Phase 3.
          </p>
          <ul className="week-view__checklist">
            <li>✓ Design tokens (styles/tokens.css)</li>
            <li>✓ API routes (api/routes.js)</li>
            <li>✓ React Query (api/queryClient.js)</li>
            <li>✓ WeekView shell (this component)</li>
          </ul>
        </div>
      </section>

      {/* WEEK ACTIONS - Placeholder for Phase 3 */}
      <footer className="week-view__actions">
        <button className="week-view__action-button week-view__action-button--secondary" disabled>
          Regenerate Week
        </button>
        <button className="week-view__action-button week-view__action-button--primary" disabled>
          Add Workout
        </button>
      </footer>
    </div>
  )
}

export default WeekView
