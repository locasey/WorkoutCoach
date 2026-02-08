/**
 * WeekNav Component
 *
 * Navigation controls for week traversal.
 * Shows previous/next buttons and current week indicator.
 *
 * @see docs/PHASE3_HANDOFF.md - Component specifications
 */

import React from 'react'
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react'
import { parseLocalDate } from '../../utils/dateUtils'
import './WeekNav.css'

/**
 * WeekNav - Week navigation controls
 *
 * @param {Object} props
 * @param {number} props.weekOffset - Current week offset (0 = this week)
 * @param {Function} props.onWeekChange - Callback when week changes
 * @param {string} [props.weekStart] - Week start date (ISO string)
 * @param {string} [props.weekEnd] - Week end date (ISO string)
 * @param {boolean} [props.disableNext] - Disable the next week button
 * @param {boolean} [props.disablePrevious] - Disable the previous week button
 */
export function WeekNav({
  weekOffset = 0,
  onWeekChange,
  weekStart,
  weekEnd,
  disableNext = false,
  disablePrevious = false,
}) {
  const isCurrentWeek = weekOffset === 0

  /**
   * Format date range for display (e.g., "Feb 3 - 9")
   */
  const formatWeekRange = () => {
    if (!weekStart || !weekEnd) return null

    const start = parseLocalDate(weekStart)
    const end = parseLocalDate(weekEnd)

    const startMonth = start.toLocaleDateString('en-US', { month: 'short' })
    const endMonth = end.toLocaleDateString('en-US', { month: 'short' })

    // If same month, show "Feb 3 - 9", otherwise "Feb 28 - Mar 6"
    if (startMonth === endMonth) {
      return `${startMonth} ${start.getDate()} - ${end.getDate()}`
    }

    return `${startMonth} ${start.getDate()} - ${endMonth} ${end.getDate()}`
  }

  const weekRange = formatWeekRange()

  /**
   * Get label for current week indicator
   */
  const getWeekLabel = () => {
    if (isCurrentWeek) return 'This Week'
    if (weekOffset === -1) return 'Last Week'
    if (weekOffset === 1) return 'Next Week'
    if (weekOffset < 0) return `${Math.abs(weekOffset)} Weeks Ago`
    return `In ${weekOffset} Weeks`
  }

  return (
    <nav className="week-nav" aria-label="Week navigation">
      {/* Previous Week Button */}
      <button
        className="week-nav__button"
        onClick={() => onWeekChange?.(weekOffset - 1)}
        disabled={disablePrevious}
        aria-label="Previous week"
      >
        <ChevronLeft className="week-nav__icon" aria-hidden="true" />
        <span className="week-nav__button-text">Previous</span>
      </button>

      {/* Current Week Indicator — clickable when not on current week */}
      <button
        className={`week-nav__current ${isCurrentWeek ? 'week-nav__current--active' : ''}`}
        onClick={() => !isCurrentWeek && onWeekChange?.(0)}
        disabled={isCurrentWeek}
        title={isCurrentWeek ? undefined : 'Return to current week'}
        aria-label={isCurrentWeek ? getWeekLabel() : 'Return to current week'}
      >
        <Calendar className="week-nav__current-icon" aria-hidden="true" />
        <div className="week-nav__current-info">
          <span className="week-nav__current-label">{getWeekLabel()}</span>
          {weekRange && <span className="week-nav__current-range">{weekRange}</span>}
        </div>
      </button>

      {/* Next Week Button */}
      <button
        className="week-nav__button"
        onClick={() => onWeekChange?.(weekOffset + 1)}
        disabled={disableNext}
        aria-label="Next week"
      >
        <span className="week-nav__button-text">Next</span>
        <ChevronRight className="week-nav__icon" aria-hidden="true" />
      </button>
    </nav>
  )
}

export default WeekNav
