import React, { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { LogOut } from 'lucide-react'
import { API_ROUTES } from '../api/routes'
import { queryKeys } from '../api/queryClient'
import { useToast } from './Toast'
import './ProfilePage.css'

const DAYS = [
  { key: 'mon', label: 'Mon' },
  { key: 'tue', label: 'Tue' },
  { key: 'wed', label: 'Wed' },
  { key: 'thu', label: 'Thu' },
  { key: 'fri', label: 'Fri' },
  { key: 'sat', label: 'Sat' },
  { key: 'sun', label: 'Sun' },
]

const EXPERIENCE_LEVELS = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' },
]

export default function ProfilePage({ onLogout }) {
  const { showToast } = useToast()

  const [availableDays, setAvailableDays] = useState([])
  const [experienceLevel, setExperienceLevel] = useState('beginner')
  const [weeklyMileage, setWeeklyMileage] = useState('')

  // Fetch user profile (includes preferences)
  const { data: profileData, isLoading } = useQuery({
    queryKey: queryKeys.user.profile,
    queryFn: async () => {
      const response = await axios.get(API_ROUTES.USER.PROFILE)
      return response.data
    },
  })

  // Populate form when profile data loads
  useEffect(() => {
    if (profileData?.user?.preferences) {
      const prefs = profileData.user.preferences
      setAvailableDays(prefs.available_days || [])
      setExperienceLevel(prefs.experience_level || 'beginner')
      setWeeklyMileage(
        prefs.weekly_mileage_comfort != null ? String(prefs.weekly_mileage_comfort) : ''
      )
    }
  }, [profileData])

  // Save preferences mutation
  const { mutate: savePreferences, isPending: isSaving } = useMutation({
    mutationFn: async (preferences) => {
      const response = await axios.put(API_ROUTES.USER.PREFERENCES, preferences)
      return response.data
    },
    onSuccess: () => {
      showToast('Preferences saved', 'success')
    },
    onError: (err) => {
      const message =
        err?.response?.data?.error || 'Failed to save preferences'
      showToast(message, 'error')
    },
  })

  const handleDayToggle = (dayKey) => {
    setAvailableDays((prev) =>
      prev.includes(dayKey)
        ? prev.filter((d) => d !== dayKey)
        : [...prev, dayKey]
    )
  }

  const handleSave = () => {
    savePreferences({
      available_days: availableDays,
      experience_level: experienceLevel,
      weekly_mileage_comfort:
        weeklyMileage !== '' ? parseFloat(weeklyMileage) : null,
    })
  }

  if (isLoading) {
    return (
      <div className="profile-page profile-page--loading">
        <div className="profile-page__spinner" />
      </div>
    )
  }

  const user = profileData?.user || {}

  return (
    <div className="profile-page">
      {/* Account section — read-only fields from Google */}
      <section className="profile-page__section">
        <h2 className="profile-page__section-title">Account</h2>

        <div className="profile-page__field">
          <span className="profile-page__label">Name</span>
          <span className="profile-page__value">
            {user.name || '\u2014'}
          </span>
        </div>

        <div className="profile-page__field">
          <span className="profile-page__label">Email</span>
          <span className="profile-page__value">
            {user.email || '\u2014'}
          </span>
        </div>
      </section>

      {/* Training Preferences section */}
      <section className="profile-page__section">
        <h2 className="profile-page__section-title">Training Preferences</h2>

        {/* Available training days */}
        <div className="profile-page__field profile-page__field--stacked">
          <span className="profile-page__label">Available Training Days</span>
          <div className="profile-page__days">
            {DAYS.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                className={`profile-page__day-btn${availableDays.includes(key) ? ' profile-page__day-btn--active' : ''}`}
                onClick={() => handleDayToggle(key)}
                aria-pressed={availableDays.includes(key)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Experience level */}
        <div className="profile-page__field profile-page__field--stacked">
          <label className="profile-page__label" htmlFor="experience-level">
            Experience Level
          </label>
          <select
            id="experience-level"
            className="profile-page__select"
            value={experienceLevel}
            onChange={(e) => setExperienceLevel(e.target.value)}
          >
            {EXPERIENCE_LEVELS.map(({ value, label }) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {/* Weekly mileage */}
        <div className="profile-page__field profile-page__field--stacked">
          <label className="profile-page__label" htmlFor="weekly-mileage">
            Weekly Mileage Comfort (km)
          </label>
          <input
            id="weekly-mileage"
            type="number"
            className="profile-page__input"
            min="0"
            step="1"
            placeholder="e.g. 40"
            value={weeklyMileage}
            onChange={(e) => setWeeklyMileage(e.target.value)}
          />
        </div>

        <button
          className="profile-page__save-btn"
          onClick={handleSave}
          disabled={isSaving}
        >
          {isSaving ? 'Saving...' : 'Save Preferences'}
        </button>
      </section>

      {/* Sign out */}
      <section className="profile-page__section profile-page__section--footer">
        <button
          className="profile-page__logout-btn logout-button"
          onClick={onLogout}
          aria-label="Sign out"
        >
          <LogOut className="w-5 h-5" aria-hidden />
          <span>Sign Out</span>
        </button>
      </section>
    </div>
  )
}
