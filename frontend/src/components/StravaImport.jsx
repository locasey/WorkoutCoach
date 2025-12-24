import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './StravaImport.css'

function StravaImport() {
  const [authUrl, setAuthUrl] = useState(null)
  const [accessToken, setAccessToken] = useState(null)
  const [activities, setActivities] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Check for token from OAuth callback
    const urlParams = new URLSearchParams(window.location.search)
    if (urlParams.get('strava_connected')) {
      const token = localStorage.getItem('strava_access_token')
      if (token) {
        setAccessToken(token)
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname)
      }
    }

    // Listen for token from popup window
    const handleMessage = (event) => {
      if (event.data.type === 'strava_token') {
        localStorage.setItem('strava_access_token', event.data.token)
        setAccessToken(event.data.token)
      }
    }
    window.addEventListener('message', handleMessage)
    
    // Check for existing token
    const existingToken = localStorage.getItem('strava_access_token')
    if (existingToken) {
      setAccessToken(existingToken)
    }

    return () => {
      window.removeEventListener('message', handleMessage)
    }
  }, [])

  const handleAuth = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/strava/auth')
      setAuthUrl(response.data.auth_url)
      // Redirect to Strava
      window.location.href = response.data.auth_url
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to initiate Strava authentication')
      setLoading(false)
    }
  }

  const handleFetchActivities = async () => {
    if (!accessToken) {
      setError('Please authenticate with Strava first')
      return
    }

    try {
      setLoading(true)
      setError(null)
      const response = await axios.get('/api/strava/activities', {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      })
      setActivities(response.data.activities)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch activities')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatPace = (speedKmh) => {
    if (!speedKmh || speedKmh === 0) return 'N/A'
    const paceMinPerKm = 60 / speedKmh
    const minutes = Math.floor(paceMinPerKm)
    const seconds = Math.round((paceMinPerKm - minutes) * 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}/km`
  }

  return (
    <div className="strava-import">
      <h2>📊 Import Strava Activities</h2>
      <p className="description">
        Connect your Strava account to import and view your training activities.
      </p>

      {!accessToken && (
        <div className="auth-section">
          <button
            onClick={handleAuth}
            disabled={loading}
            className="auth-button"
          >
            {loading ? 'Connecting...' : '🔗 Connect to Strava'}
          </button>
          {authUrl && (
            <p className="info-text">
              Redirecting to Strava for authentication...
            </p>
          )}
        </div>
      )}

      {accessToken && (
        <div className="authenticated-section">
          <div className="status-badge">
            ✅ Connected to Strava
          </div>
          <button
            onClick={handleFetchActivities}
            disabled={loading}
            className="fetch-button"
          >
            {loading ? 'Loading...' : '📥 Fetch Activities'}
          </button>
        </div>
      )}

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {activities.length > 0 && (
        <div className="activities-section">
          <h3>Your Activities ({activities.length})</h3>
          <div className="activities-table-container">
            <table className="activities-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Distance</th>
                  <th>Time</th>
                  <th>Pace</th>
                  <th>Heart Rate</th>
                </tr>
              </thead>
              <tbody>
                {activities.map((activity) => (
                  <tr key={activity.id}>
                    <td>{formatDate(activity.start_date)}</td>
                    <td className="activity-name">{activity.name}</td>
                    <td>{activity.type}</td>
                    <td>{activity.distance.toFixed(2)} km</td>
                    <td>{Math.round(activity.moving_time)} min</td>
                    <td>{formatPace(activity.average_speed)}</td>
                    <td>{activity.average_heartrate ? `${activity.average_heartrate} bpm` : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activities.length === 0 && accessToken && !loading && (
        <div className="empty-state">
          <p>No activities loaded yet. Click "Fetch Activities" to import your Strava data.</p>
        </div>
      )}
    </div>
  )
}

export default StravaImport

