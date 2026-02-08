/**
 * WeekActions Component
 *
 * Action buttons for the weekly view footer.
 * Provides regenerate and add workout functionality.
 *
 * @see docs/PHASE3_HANDOFF.md - Component specifications
 */

import React from 'react'
import { RefreshCw, Plus } from 'lucide-react'
import './WeekActions.css'

/**
 * WeekActions - Week-level action buttons
 *
 * @param {Object} props
 * @param {Function} [props.onRegenerate] - Callback to regenerate week's workouts
 * @param {Function} [props.onAddWorkout] - Callback to add a new workout
 * @param {boolean} [props.isRegenerating] - Whether regeneration is in progress
 * @param {boolean} [props.disabled] - Disable all actions
 * @param {'training'|'maintenance'} [props.mode] - Current operating mode
 */
export function WeekActions({
  onRegenerate,
  onAddWorkout,
  isRegenerating = false,
  disabled = false,
  mode = 'maintenance',
}) {
  const isTrainingMode = mode === 'training'

  return (
    <footer className="week-actions">
      {/* Regenerate Week Button */}
      <button
        className="week-actions__button week-actions__button--secondary"
        onClick={onRegenerate}
        disabled={disabled || isRegenerating}
        aria-label="Regenerate this week's workouts"
      >
        <RefreshCw
          className={`week-actions__icon ${isRegenerating ? 'week-actions__icon--spinning' : ''}`}
          aria-hidden="true"
        />
        <span>{isRegenerating ? 'Regenerating...' : 'Regenerate Week'}</span>
      </button>

      {/* Add Workout Button */}
      <button
        className="week-actions__button week-actions__button--primary"
        onClick={onAddWorkout}
        disabled={disabled}
        aria-label="Add a new workout"
      >
        <Plus className="week-actions__icon" aria-hidden="true" />
        <span>Add Workout</span>
      </button>
    </footer>
  )
}

export default WeekActions
