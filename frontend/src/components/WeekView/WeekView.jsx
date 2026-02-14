/**
 * WeekView Component
 *
 * Unified weekly view that replaces WeekAheadView.
 * Supports both Training Block mode and Maintenance mode.
 * Uses React Query for data fetching and caching.
 *
 * Architecture:
 *   WeekView (this component)
 *   ├── WeekHeader - Shows phase/mode context
 *   ├── WeekNav - Previous/Next week navigation
 *   ├── DayCard[] - 7 day cards with workouts
 *   │   └── WorkoutCard - Individual workout display
 *   └── WeekActions - Regenerate, Add Workout buttons
 *
 * @see docs/PHASE3_HANDOFF.md - Phase 3 specifications
 * @see docs/ARCHITECTURE_ROADMAP.md - Target Frontend Architecture
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { Target, AlertCircle } from 'lucide-react'

import { WeekHeader } from './WeekHeader'
import { WeekNav } from './WeekNav'
import { DayCard } from './DayCard'
import { WeekActions } from './WeekActions'
import { WorkoutEditModal } from '../WorkoutEditModal'
import { RegenerateModal } from '../RegenerateModal'
import { useToast } from '../Toast'

import { queryKeys } from '../../api/queryClient'
import { API_ROUTES, buildUrl } from '../../api/routes'
import { mapWorkoutToDesign, formatWorkoutType, formatDistance } from '../../utils/workoutMapper'
import { parseLocalDate } from '../../utils/dateUtils'

import './WeekView.css'

/**
 * Generate array of dates for the week
 * @param {string} weekStart - ISO date string for Monday
 * @returns {string[]} Array of 7 ISO date strings
 */
const generateWeekDates = (weekStart) => {
  if (!weekStart) {
    // Fallback: generate from current week
    const today = new Date()
    const dayOfWeek = today.getDay()
    const monday = new Date(today)
    monday.setDate(today.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1))

    return Array.from({ length: 7 }, (_, i) => {
      const date = new Date(monday)
      date.setDate(monday.getDate() + i)
      return date.toISOString().split('T')[0]
    })
  }

  const start = parseLocalDate(weekStart)
  return Array.from({ length: 7 }, (_, i) => {
    const date = new Date(start)
    date.setDate(start.getDate() + i)
    return date.toISOString().split('T')[0]
  })
}

/**
 * Group workouts by date
 * @param {Array} workouts - Array of workout objects
 * @returns {Object} Map of date string to workout array
 */
const groupWorkoutsByDate = (workouts = []) => {
  const grouped = {}

  workouts.forEach((workout) => {
    const date = workout.scheduled_date || workout.scheduledDate
    if (!date) return

    if (!grouped[date]) {
      grouped[date] = []
    }
    grouped[date].push(workout)

    // Sort by slot (null first, then 1=AM, then 2=PM)
    grouped[date].sort((a, b) => (a.slot || 0) - (b.slot || 0))
  })

  return grouped
}

/**
 * WeekView - Main weekly training view
 *
 * @param {Object} props
 * @param {number} [props.weekOffset=0] - Week offset from current (0 = this week)
 * @param {Function} [props.onWeekChange] - Callback when week changes
 */
export function WeekView({
  weekOffset: initialOffset = 0,
  onWeekChange,
  onStartTraining,
  showRegenerate: showRegenerateProp,
  setShowRegenerate: setShowRegenerateProp,
  unit = 'mi',
}) {
  const queryClient = useQueryClient()
  const toast = useToast()

  // Local state
  const [weekOffset, setWeekOffset] = useState(initialOffset)
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [selectedWorkout, setSelectedWorkout] = useState(null)

  // Mobile responsive state
  const [isMobile, setIsMobile] = useState(
    typeof window !== 'undefined' && window.innerWidth < 768
  )
  const [selectedDayIndex, setSelectedDayIndex] = useState(null)

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Regenerate modal state - use props if provided (lifted from App.jsx), else local
  const [localShowRegenerate, localSetShowRegenerate] = useState(false)
  const showRegenerate = showRegenerateProp !== undefined ? showRegenerateProp : localShowRegenerate
  const setShowRegenerate = setShowRegenerateProp || localSetShowRegenerate

  /**
   * Fetch week data from API
   * Uses the unified /api/week endpoint
   */
  const {
    data: weekData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: queryKeys.week.byOffset(weekOffset),
    queryFn: async () => {
      const url = buildUrl(API_ROUTES.WEEK.CURRENT, { offset: weekOffset })
      const response = await axios.get(url)
      return response.data
    },
    staleTime: 30 * 1000, // 30 seconds
  })

  /**
   * Toggle workout completion mutation
   */
  const toggleCompleteMutation = useMutation({
    mutationFn: async (workoutId) => {
      const response = await axios.put(API_ROUTES.WORKOUTS.COMPLETE(workoutId))
      return response.data
    },
    onSuccess: () => {
      // Invalidate and refetch week data
      queryClient.invalidateQueries({ queryKey: queryKeys.week.byOffset(weekOffset) })
    },
  })

  /**
   * Add workout mutation
   */
  const addWorkoutMutation = useMutation({
    mutationFn: async ({ scheduledDate, type = 'easy_run' }) => {
      const response = await axios.post(API_ROUTES.WORKOUTS.ADD_TO_DAY, {
        training_block_id: weekData?.block_id,
        scheduled_date: scheduledDate,
        type,
        duration_minutes: 30,
        notes: 'New workout',
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.week.byOffset(weekOffset) })
    },
  })

  /**
   * Regenerate week mutation
   */
  const regenerateMutation = useMutation({
    mutationFn: async ({ weekOffset: offset, reason }) => {
      const response = await axios.post(API_ROUTES.WEEK.REGENERATE, {
        week_offset: offset,
        reason,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.week.byOffset(weekOffset) })
      setShowRegenerate(false)
      toast.success('Week regenerated!')
    },
    onError: (err) => {
      toast.error(err.response?.data?.error || 'Failed to regenerate week')
    },
  })

  /**
   * Delete workout mutation
   */
  const deleteWorkoutMutation = useMutation({
    mutationFn: async (workoutId) => {
      const response = await axios.delete(API_ROUTES.WORKOUTS.BY_ID(workoutId))
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.week.byOffset(weekOffset) })
      setEditModalOpen(false)
      setSelectedWorkout(null)
      toast.success('Workout deleted')
    },
    onError: (err) => {
      toast.error(err.response?.data?.error || 'Failed to delete workout')
    },
  })

  /**
   * Handle week navigation
   */
  const handleWeekChange = useCallback(
    (newOffset) => {
      setWeekOffset(newOffset)
      onWeekChange?.(newOffset)
    },
    [onWeekChange]
  )

  /**
   * Handle workout click - open edit modal
   */
  const handleWorkoutClick = useCallback(
    (workoutId) => {
      const workout = weekData?.workouts?.find((w) => w.id === workoutId)
      if (workout) {
        setSelectedWorkout(mapWorkoutToDesign(workout, unit))
        setEditModalOpen(true)
      }
    },
    [weekData]
  )

  /**
   * Handle toggle complete
   */
  const handleToggleComplete = useCallback(
    (workoutId) => {
      toggleCompleteMutation.mutate(workoutId)
    },
    [toggleCompleteMutation]
  )

  /**
   * Handle add workout to day
   */
  const handleAddWorkoutToDay = useCallback(
    (date) => {
      addWorkoutMutation.mutate({ scheduledDate: date })
    },
    [addWorkoutMutation]
  )

  /**
   * Handle delete workout
   */
  const handleDeleteWorkout = useCallback(
    (workoutId) => {
      deleteWorkoutMutation.mutate(workoutId)
    },
    [deleteWorkoutMutation]
  )

  /**
   * Handle save from edit modal
   */
  const handleSaveWorkout = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: queryKeys.week.byOffset(weekOffset) })
    setEditModalOpen(false)
    setSelectedWorkout(null)
  }, [queryClient, weekOffset])

  /**
   * Derive display data
   */
  const weekDates = useMemo(
    () => generateWeekDates(weekData?.week_start),
    [weekData?.week_start]
  )

  const workoutsByDate = useMemo(
    () => groupWorkoutsByDate(weekData?.workouts),
    [weekData?.workouts]
  )

  const isTrainingMode = weekData?.mode === 'training'
  const hasWorkouts = weekData?.workouts?.length > 0

  // Default selectedDayIndex to today for current week, or Monday otherwise
  useEffect(() => {
    if (!weekDates.length) return
    if (weekOffset === 0) {
      const todayStr = new Date().toISOString().split('T')[0]
      const todayIdx = weekDates.indexOf(todayStr)
      setSelectedDayIndex(todayIdx >= 0 ? todayIdx : 0)
    } else {
      setSelectedDayIndex(0)
    }
  }, [weekData?.week_start, weekOffset])

  /* =========================================================================
   * RENDER - Loading State
   * ========================================================================= */
  if (isLoading) {
    return (
      <div className="week-view">
        <div className="week-view__loading">
          <div className="week-view__loading-spinner" />
          <p>Loading week...</p>
        </div>
      </div>
    )
  }

  /* =========================================================================
   * RENDER - Error State
   * ========================================================================= */
  if (isError) {
    return (
      <div className="week-view">
        <div className="week-view__error">
          <AlertCircle className="week-view__error-icon" aria-hidden="true" />
          <h2>Unable to load week</h2>
          <p>{error?.message || 'Something went wrong'}</p>
          <button className="week-view__error-retry" onClick={() => refetch()}>
            Try Again
          </button>
        </div>
      </div>
    )
  }

  /* =========================================================================
   * RENDER - Empty State (No active plan)
   * ========================================================================= */
  if (!hasWorkouts && !isTrainingMode) {
    return (
      <div className="week-view">
        <WeekHeader mode="maintenance" weekStart={weekData?.week_start} weekEnd={weekData?.week_end} />
        <WeekNav
          weekOffset={weekOffset}
          onWeekChange={handleWeekChange}
          weekStart={weekData?.week_start}
          weekEnd={weekData?.week_end}
        />
        <div className="week-view__empty">
          <Target className="week-view__empty-icon" aria-hidden="true" />
          <h2>Maintenance Mode</h2>
          <p>You're in flexible training mode — no rigid plan, just staying fit.</p>
          {onStartTraining && (
            <button className="week-view__empty-cta" onClick={onStartTraining}>
              Start Training Block
            </button>
          )}
        </div>
        <WeekActions mode="maintenance" disabled />
      </div>
    )
  }

  /* =========================================================================
   * RENDER - Main View
   * ========================================================================= */
  return (
    <div className="week-view">
      {/* Header with phase/mode context */}
      <WeekHeader
        mode={weekData?.mode || 'maintenance'}
        weekNumber={weekData?.week_number}
        totalWeeks={weekData?.total_weeks}
        phase={weekData?.phase}
        weeksUntilRace={weekData?.weeks_until_race}
        eventName={weekData?.event_name}
        weekStart={weekData?.week_start}
        weekEnd={weekData?.week_end}
      />

      {/* Week Navigation */}
      <WeekNav
        weekOffset={weekOffset}
        onWeekChange={handleWeekChange}
        weekStart={weekData?.week_start}
        weekEnd={weekData?.week_end}
      />

      {/* Mobile: Day Picker + Hero */}
      {isMobile ? (
        <>
          <nav className="week-view__day-picker" aria-label="Day selector">
            {weekDates.map((date, idx) => {
              const d = parseLocalDate(date)
              const dayName = d.toLocaleDateString('en-US', { weekday: 'short' })
              const dayNum = d.getDate()
              const todayStr = new Date().toISOString().split('T')[0]
              const isToday = date === todayStr
              const dayWorkouts = workoutsByDate[date] || []
              const isRaceDayPill = weekData?.target_date && date === weekData.target_date
              const metric = isRaceDayPill
                ? '🏁'
                : dayWorkouts.length > 0
                  ? dayWorkouts[0].distance_km
                    ? formatDistance(dayWorkouts[0].distance_km, unit)
                    : dayWorkouts[0].duration_minutes
                      ? `${dayWorkouts[0].duration_minutes}m`
                      : formatWorkoutType(dayWorkouts[0].type) || 'Rest'
                  : 'Rest'

              return (
                <button
                  key={date}
                  className={`week-view__day-pill${selectedDayIndex === idx ? ' week-view__day-pill--active' : ''}${isToday ? ' week-view__day-pill--today' : ''}`}
                  onClick={() => setSelectedDayIndex(idx)}
                  aria-label={`${dayName} ${dayNum}`}
                  aria-selected={selectedDayIndex === idx}
                >
                  <span className="week-view__day-pill-name">{dayName}</span>
                  <span className="week-view__day-pill-num">{dayNum}</span>
                  <span className="week-view__day-pill-metric">{metric}</span>
                </button>
              )
            })}
          </nav>

          {selectedDayIndex !== null && weekDates[selectedDayIndex] && (
            <section className="week-view__day-hero" aria-label="Selected day">
              <DayCard
                date={weekDates[selectedDayIndex]}
                workouts={workoutsByDate[weekDates[selectedDayIndex]] || []}
                onWorkoutClick={handleWorkoutClick}
                onToggleComplete={handleToggleComplete}
                onAddWorkout={handleAddWorkoutToDay}
                canAddWorkout={weekData?.block_id != null}
                targetDate={weekData?.target_date}
                unit={unit}
              />
            </section>
          )}
        </>
      ) : (
        /* Desktop: 7-column grid */
        <section className="week-view__days-grid" aria-label="Weekly workouts">
          {weekDates.map((date) => (
            <DayCard
              key={date}
              date={date}
              workouts={workoutsByDate[date] || []}
              onWorkoutClick={handleWorkoutClick}
              onToggleComplete={handleToggleComplete}
              onAddWorkout={handleAddWorkoutToDay}
              canAddWorkout={weekData?.block_id != null}
              targetDate={weekData?.target_date}
              unit={unit}
            />
          ))}
        </section>
      )}

      {/* Week Actions */}
      <WeekActions
        mode={weekData?.mode || 'maintenance'}
        onRegenerate={() => setShowRegenerate(true)}
        isRegenerating={regenerateMutation.isPending}
        onAddWorkout={() => {
          /* Could open a date picker or add to today */
        }}
        disabled={!weekData?.block_id}
      />

      {/* Regenerate Modal */}
      <RegenerateModal
        isOpen={showRegenerate}
        onClose={() => setShowRegenerate(false)}
        onConfirm={(reason) =>
          regenerateMutation.mutate({ weekOffset, reason })
        }
        isRegenerating={regenerateMutation.isPending}
        weekNumber={weekData?.week_number}
        phase={weekData?.phase}
      />

      {/* Edit Modal */}
      <WorkoutEditModal
        isOpen={editModalOpen}
        onClose={() => {
          setEditModalOpen(false)
          setSelectedWorkout(null)
        }}
        workout={selectedWorkout}
        onSave={handleSaveWorkout}
        onDelete={handleDeleteWorkout}
        unit={unit}
      />
    </div>
  )
}

export default WeekView
