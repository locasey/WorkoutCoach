/**
 * WeekView Component Exports
 *
 * Re-exports all WeekView-related components for clean imports.
 *
 * Usage:
 *   import { WeekView } from './components/WeekView'
 *   import { WeekView, WeekHeader, DayCard } from './components/WeekView'
 *
 * Components:
 *   - WeekView: Main container with React Query integration
 *   - WeekHeader: Phase/mode context display
 *   - WeekNav: Previous/Next week navigation
 *   - DayCard: Single day container with workouts
 *   - WeekActions: Regenerate, Add Workout buttons
 */

export { WeekView } from './WeekView'
export { WeekHeader } from './WeekHeader'
export { WeekNav } from './WeekNav'
export { DayCard } from './DayCard'
export { WeekActions } from './WeekActions'

export { default } from './WeekView'
