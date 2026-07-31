import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { ChevronLeft } from 'lucide-react'
import { API_ROUTES } from '../../api/routes'
import { queryKeys } from '../../api/queryClient'

const DAYS = [
  { key: 'mon', label: 'Mon' }, { key: 'tue', label: 'Tue' }, { key: 'wed', label: 'Wed' },
  { key: 'thu', label: 'Thu' }, { key: 'fri', label: 'Fri' }, { key: 'sat', label: 'Sat' }, { key: 'sun', label: 'Sun' },
]

const EXPERIENCE_LEVELS = [
  { value: 'beginner', label: 'Beginner', desc: 'New to running or returning after a long break' },
  { value: 'intermediate', label: 'Intermediate', desc: 'Running regularly, completed a few races' },
  { value: 'advanced', label: 'Advanced', desc: 'Experienced racer, training 5+ days/week' },
]

/**
 * MaintenanceDetails - Step for "Just Staying Fit" flow
 *
 * Collects available_days + experience_level, pre-filled from the user's
 * saved preferences (unlike RaceDetails, which is always blank). No
 * event/distance/date fields — maintenance mode has an indefinite timeline.
 */
export function MaintenanceDetails({ onBack, onNext, isSubmitting = false }) {
  const { data: profileData } = useQuery({
    queryKey: queryKeys.user.profile,
    queryFn: async () => (await axios.get(API_ROUTES.USER.PROFILE)).data,
  })

  const [availableDays, setAvailableDays] = useState([])
  const [experienceLevel, setExperienceLevel] = useState('intermediate')

  useEffect(() => {
    const prefs = profileData?.user?.preferences
    if (prefs) {
      if (prefs.available_days?.length) setAvailableDays(prefs.available_days)
      if (prefs.experience_level) setExperienceLevel(prefs.experience_level)
    }
  }, [profileData])

  const handleDayToggle = (dayKey) => {
    setAvailableDays((prev) =>
      prev.includes(dayKey) ? prev.filter((d) => d !== dayKey) : [...prev, dayKey]
    )
  }

  const isValid = availableDays.length > 0

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!isValid || isSubmitting) return
    onNext({ available_days: availableDays, experience_level: experienceLevel })
  }

  return (
    <div className="goal-setup__step">
      <button className="goal-setup__back-btn" onClick={onBack} type="button" disabled={isSubmitting}>
        <ChevronLeft size={20} aria-hidden />
        Back
      </button>

      <h2 className="goal-setup__step-title">Set up your maintenance week</h2>
      <p className="goal-setup__step-desc">
        No rigid plan — just tell us what you've got, and we'll suggest a sustainable weekly rhythm.
      </p>

      <form className="goal-setup__form" onSubmit={handleSubmit}>
        <div className="goal-setup__field">
          <label>Which days can you train?</label>
          <div className="goal-setup__day-picker">
            {DAYS.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                className={`goal-setup__day-btn${availableDays.includes(key) ? ' goal-setup__day-btn--active' : ''}`}
                onClick={() => handleDayToggle(key)}
                aria-pressed={availableDays.includes(key)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <div className="goal-setup__field">
          <label>Experience Level</label>
          <div className="goal-setup__radio-group">
            {EXPERIENCE_LEVELS.map((level) => (
              <label
                key={level.value}
                className={`goal-setup__radio-card ${experienceLevel === level.value ? 'goal-setup__radio-card--selected' : ''}`}
              >
                <input
                  type="radio"
                  name="experience"
                  value={level.value}
                  checked={experienceLevel === level.value}
                  onChange={(e) => setExperienceLevel(e.target.value)}
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
          disabled={!isValid || isSubmitting}
        >
          {isSubmitting ? 'Generating your week...' : 'Generate My Week'}
        </button>
      </form>
    </div>
  )
}

export default MaintenanceDetails
