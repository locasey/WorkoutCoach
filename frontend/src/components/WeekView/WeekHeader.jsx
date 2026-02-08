import React from 'react'
import { parseLocalDate } from '../../utils/dateUtils'
import './WeekHeader.css'

const capitalize = (str) => {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

export function WeekHeader({
  mode = 'maintenance',
  weekNumber,
  totalWeeks,
  phase,
  weeksUntilRace,
  eventName,
  weekStart,
  weekEnd,
}) {
  const isTrainingMode = mode === 'training'

  const formatDateRange = () => {
    if (!weekStart || !weekEnd) return null

    const start = parseLocalDate(weekStart)
    const end = parseLocalDate(weekEnd)

    const startStr = start.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    })

    const endStr = end.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })

    return `${startStr} - ${endStr}`
  }

  const dateRange = formatDateRange()

  return (
    <header className="week-header">
      <div className="week-header__content">
        {isTrainingMode ? (
          <>
            <h1 className="week-header__title">
              Week {weekNumber}{totalWeeks && ` / ${totalWeeks}`}
              {phase && <span className="week-header__phase" data-phase={phase}> &middot; {capitalize(phase)} Phase</span>}
            </h1>

            {weeksUntilRace !== undefined && eventName && (
              <p className="week-header__countdown">
                {weeksUntilRace} {weeksUntilRace === 1 ? 'week' : 'weeks'} to {eventName}
              </p>
            )}

            {dateRange && (
              <p className="week-header__dates">{dateRange}</p>
            )}
          </>
        ) : (
          <>
            <div className="week-header__maintenance-row">
              <h1 className="week-header__title">This Week</h1>
              {dateRange && (
                <span className="week-header__dates week-header__dates--inline">{dateRange}</span>
              )}
            </div>
            <p className="week-header__subtitle">Just Staying Fit</p>
          </>
        )}
      </div>
    </header>
  )
}

export default WeekHeader
