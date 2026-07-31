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
 * @param {Function} [props.onRegenerate] - Callback to regenerate/generate week's workouts
 * @param {Function} [props.onAddWorkout] - Callback to add a new workout
 * @param {boolean} [props.isRegenerating] - Whether regeneration/generation is in progress
 * @param {boolean} [props.regenerateDisabled] - Disable the regenerate/generate button
 * @param {boolean} [props.addDisabled] - Disable the add workout button
 * @param {boolean} [props.hasWorkouts] - Whether this week already has workouts (flips button label)
 * @param {'training'|'maintenance'} [props.mode] - Current operating mode
 */
export function WeekActions({
  onRegenerate,
  onAddWorkout,
  isRegenerating = false,
  regenerateDisabled = false,
  addDisabled = false,
  hasWorkouts = true,
  mode = 'maintenance',
}) {
  return (
    <footer className="week-actions">
      {/* Regenerate/Generate Week Button */}
      <button
        className="week-actions__button week-actions__button--secondary"
        onClick={onRegenerate}
        disabled={regenerateDisabled || isRegenerating}
        aria-label={hasWorkouts ? "Regenerate this week's workouts" : "Generate this week's workouts"}
      >
        <RefreshCw
          className={`week-actions__icon ${isRegenerating ? 'week-actions__icon--spinning' : ''}`}
          aria-hidden="true"
        />
        <span>
          {isRegenerating
            ? (hasWorkouts ? 'Regenerating...' : 'Generating...')
            : (hasWorkouts ? 'Regenerate Week' : 'Generate This Week')}
        </span>
      </button>

      {/* Add Workout Button */}
      <button
        className="week-actions__button week-actions__button--primary"
        onClick={onAddWorkout}
        disabled={addDisabled}
        aria-label="Add a new workout"
      >
        <Plus className="week-actions__icon" aria-hidden="true" />
        <span>Add Workout</span>
      </button>
    </footer>
  )
}

export default WeekActions
