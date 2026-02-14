/**
 * DayCard Component
 *
 * Displays a single day with its workout(s) in the weekly view.
 * Supports single workouts, AM/PM slots, and empty/rest days.
 *
 * @see docs/PHASE3_HANDOFF.md - Component specifications
 */

import React from 'react'
import { Plus, Calendar } from 'lucide-react'
import { WorkoutCard } from '../WorkoutCard'
import { mapWorkoutToDesign } from '../../utils/workoutMapper'
import { parseLocalDate } from '../../utils/dateUtils'
import './DayCard.css'

/**
 * Format a date to display as "Mon 12" format
 * @param {string} dateStr - ISO date string
 * @returns {Object} Object with dayName and dayNumber
 */
const formatDayDisplay = (dateStr) => {
  if (!dateStr) return { dayName: '', dayNumber: '' }

  const date = parseLocalDate(dateStr)
  const dayName = date.toLocaleDateString('en-US', { weekday: 'short' })
  const dayNumber = date.getDate()

  return { dayName, dayNumber }
}

/**
 * Check if a date is today
 * @param {string} dateStr - ISO date string
 * @returns {boolean}
 */
const isToday = (dateStr) => {
  if (!dateStr) return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const date = parseLocalDate(dateStr)
  return today.getTime() === date.getTime()
}

/**
 * DayCard - Single day container with workout(s)
 *
 * @param {Object} props
 * @param {string} props.date - ISO date string for this day
 * @param {Array} props.workouts - Array of workout objects for this day (0-2)
 * @param {Function} props.onWorkoutClick - Callback when workout is clicked
 * @param {Function} props.onToggleComplete - Callback to toggle workout completion
 * @param {Function} props.onAddWorkout - Callback to add workout to this day
 * @param {boolean} props.canAddWorkout - Whether adding workouts is allowed (< 2 per day)
 */
export function DayCard({
  date,
  workouts = [],
  onWorkoutClick,
  onToggleComplete,
  onAddWorkout,
  canAddWorkout = true,
  targetDate,
  unit = 'mi',
}) {
  const { dayName, dayNumber } = formatDayDisplay(date)
  const isTodayDate = isToday(date)
  const isRaceDay = targetDate && date === targetDate
  const hasWorkouts = workouts.length > 0
  const hasMultiple = workouts.length > 1
  const showAddButton = !isRaceDay && canAddWorkout && workouts.length < 2

  /**
   * Map API workout format to design format if needed.
   * Detects already-mapped data by the _original property added by mapWorkoutToDesign.
   */
  const mapWorkout = (workout) => {
    if (workout._original) return workout
    return mapWorkoutToDesign(workout, unit)
  }

  return (
    <div
      className={`day-card ${isTodayDate ? 'day-card--today' : ''} ${isRaceDay ? 'day-card--race' : ''} ${!hasWorkouts && !isRaceDay ? 'day-card--empty' : ''}`}
    >
      {/* Day Header */}
      <div className="day-card__header">
        <span className="day-card__day-name">{dayName}</span>
        <span className={`day-card__day-number ${isTodayDate ? 'day-card__day-number--today' : ''}`}>
          {dayNumber}
        </span>
        {isTodayDate && (
          <span className="day-card__today-badge">
            <Calendar className="day-card__today-icon" aria-hidden="true" />
            Today
          </span>
        )}
      </div>

      {/* Workouts Container */}
      <div className="day-card__workouts">
        {isRaceDay ? (
          /* Race Day */
          <div className="day-card__race-day">
            <span className="day-card__race-day-icon">🏁</span>
            <span className="day-card__race-day-title">Race Day</span>
            <span className="day-card__race-day-subtitle">You've got this!</span>
          </div>
        ) : hasWorkouts ? (
          <>
            {workouts.map((workout, index) => {
              const mappedWorkout = mapWorkout(workout)
              const isAM = hasMultiple && index === 0
              const isPM = hasMultiple && index === 1

              return (
                <WorkoutCard
                  key={workout.id}
                  workout={{
                    ...mappedWorkout,
                    day: '',  // DayCard header shows day — don't duplicate
                    scheduledDate: date,
                  }}
                  isToday={false}  // DayCard header shows today badge
                  isAM={isAM}
                  isPM={isPM}
                  onToggle={() => onToggleComplete?.(workout.id)}
                  onEdit={() => onWorkoutClick?.(workout.id)}
                />
              )
            })}
          </>
        ) : (
          /* Empty State */
          <div className="day-card__empty">
            <span className="day-card__empty-text">Rest day</span>
          </div>
        )}

        {/* Add Workout Button */}
        {showAddButton && (
          <button
            className="day-card__add-button"
            onClick={() => onAddWorkout?.(date)}
            aria-label={`Add workout to ${dayName}`}
          >
            <Plus className="day-card__add-icon" aria-hidden="true" />
            <span>Add</span>
          </button>
        )}
      </div>
    </div>
  )
}

export default DayCard
