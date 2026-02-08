import React, { useState, useMemo } from 'react'
import { ChevronLeft } from 'lucide-react'
import { calculateTotalWeeks } from '../../utils/phaseCalculator'

const DISTANCES = [
  { value: '5k', label: '5K' },
  { value: '10k', label: '10K' },
  { value: 'half', label: 'Half Marathon' },
  { value: 'marathon', label: 'Marathon' },
  { value: 'ultra', label: 'Ultra Marathon' },
  { value: 'other', label: 'Other' },
]

const EXPERIENCE_LEVELS = [
  { value: 'beginner', label: 'Beginner', desc: 'New to running or returning after a long break' },
  { value: 'intermediate', label: 'Intermediate', desc: 'Running regularly, completed a few races' },
  { value: 'advanced', label: 'Advanced', desc: 'Experienced racer, training 5+ days/week' },
]

/**
 * RaceDetails - Step 2 of GoalSetup wizard
 *
 * Form inputs: event name, distance, target date, experience level.
 * Auto-calculates total_weeks from today to target_date.
 */
export function RaceDetails({ onNext, onBack, initialData = {} }) {
  const [eventName, setEventName] = useState(initialData.eventName || '')
  const [distance, setDistance] = useState(initialData.distance || 'half')
  const [customDistance, setCustomDistance] = useState(initialData.customDistance || '')
  const [targetDate, setTargetDate] = useState(initialData.targetDate || '')
  const [experience, setExperience] = useState(initialData.experience || 'intermediate')

  const totalWeeks = useMemo(() => {
    if (!targetDate) return null
    return calculateTotalWeeks(targetDate)
  }, [targetDate])

  const effectiveDistance = distance === 'other' ? customDistance.trim() : distance
  const isValid = eventName.trim() && effectiveDistance && targetDate && totalWeeks >= 4 && totalWeeks <= 52

  // Minimum date = 4 weeks from today
  const minDate = useMemo(() => {
    const d = new Date()
    d.setDate(d.getDate() + 28) // 4 weeks
    return d.toISOString().split('T')[0]
  }, [])

  // Maximum date = 52 weeks from today
  const maxDate = useMemo(() => {
    const d = new Date()
    d.setDate(d.getDate() + 364) // ~52 weeks
    return d.toISOString().split('T')[0]
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!isValid) return
    onNext({ eventName, distance: effectiveDistance, customDistance, targetDate, experience, totalWeeks })
  }

  return (
    <div className="goal-setup__step">
      <button className="goal-setup__back-btn" onClick={onBack} type="button">
        <ChevronLeft size={20} aria-hidden />
        Back
      </button>

      <h2 className="goal-setup__step-title">Race Details</h2>
      <p className="goal-setup__step-desc">Tell us about your upcoming race.</p>

      <form className="goal-setup__form" onSubmit={handleSubmit}>
        <div className="goal-setup__field">
          <label htmlFor="event-name">Event Name</label>
          <input
            id="event-name"
            type="text"
            value={eventName}
            onChange={(e) => setEventName(e.target.value)}
            placeholder="e.g., Boston Marathon"
            maxLength={255}
            required
          />
        </div>

        <div className="goal-setup__field">
          <label htmlFor="distance">Distance</label>
          <select
            id="distance"
            value={distance}
            onChange={(e) => setDistance(e.target.value)}
            required
          >
            {DISTANCES.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </select>
          {distance === 'other' && (
            <input
              type="text"
              value={customDistance}
              onChange={(e) => setCustomDistance(e.target.value)}
              placeholder="e.g., 10 miles, 15K, 50K"
              maxLength={50}
              required
            />
          )}
        </div>

        <div className="goal-setup__field">
          <label htmlFor="target-date">Race Date</label>
          <input
            id="target-date"
            type="date"
            value={targetDate}
            onChange={(e) => setTargetDate(e.target.value)}
            min={minDate}
            max={maxDate}
            required
          />
          {targetDate && totalWeeks !== null && (
            <span className={`goal-setup__field-hint ${totalWeeks < 4 || totalWeeks > 52 ? 'goal-setup__field-hint--error' : ''}`}>
              {totalWeeks < 4
                ? 'Race must be at least 4 weeks away'
                : totalWeeks > 52
                  ? 'Race must be within 52 weeks'
                  : `${totalWeeks} weeks of training`}
            </span>
          )}
        </div>

        <div className="goal-setup__field">
          <label>Experience Level</label>
          <div className="goal-setup__radio-group">
            {EXPERIENCE_LEVELS.map((level) => (
              <label
                key={level.value}
                className={`goal-setup__radio-card ${experience === level.value ? 'goal-setup__radio-card--selected' : ''}`}
              >
                <input
                  type="radio"
                  name="experience"
                  value={level.value}
                  checked={experience === level.value}
                  onChange={(e) => setExperience(e.target.value)}
                  className="goal-setup__radio-input"
                />
                <span className="goal-setup__radio-label">{level.label}</span>
                <span className="goal-setup__radio-desc">{level.desc}</span>
              </label>
            ))}
          </div>
        </div>

        <button
          type="submit"
          className="goal-setup__next-btn"
          disabled={!isValid}
        >
          Preview Training Plan
        </button>
      </form>
    </div>
  )
}
