import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useToast } from './Toast'
import { ErrorAlert } from './ErrorAlert'
import './StravaImport.css'

const API_BASE_URL = '/api';

function StravaImport() {
  const [sessionToken, setSessionToken] = useState(null)
  const [athlete, setAthlete] = useState(null)
  const [activities, setActivities] = useState([])
  const [loading, setLoading] = useState(false)
  const [validating, setValidating] = useState(true)
  const [error, setError] = useState(null)
  const toast = useToast()

  // Get authorization header for API calls
  const getAuthHeader = () => {
    if (!sessionToken) return {};
    return { 'Authorization': `Bearer ${sessionToken}` };
  };

  // Validate existing session on mount
  useEffect(() => {
    const validateSession = async () => {
      // Check for token from OAuth callback (URL params)
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get('strava_connected')) {
        const token = localStorage.getItem('strava_session_token');
        if (token) {
          setSessionToken(token);
          window.history.replaceState({}, document.title, window.location.pathname);
        }
      }

      // Check for existing session token
      const existingToken = localStorage.getItem('strava_session_token');
      if (existingToken) {
        try {
          const response = await axios.get(`${API_BASE_URL}/strava/validate`, {
            headers: { 'Authorization': `Bearer ${existingToken}` }
          });

          if (response.data.valid) {
            setSessionToken(existingToken);
            setAthlete(response.data.athlete);
            // Load stored activities
            await fetchStoredActivities(existingToken);
          } else {
            // Invalid session, clear it
            localStorage.removeItem('strava_session_token');
          }
        } catch (err) {
          console.log('Session validation failed:', err.response?.data?.error);
          // Clear invalid session
          localStorage.removeItem('strava_session_token');
        }
      }
      setValidating(false);
    };

    // Listen for messages from OAuth popup
    const handleMessage = (event) => {
      if (event.data.type === 'strava_session') {
        const { sessionToken: newToken, athlete: athleteData } = event.data;
        localStorage.setItem('strava_session_token', newToken);
        setSessionToken(newToken);
        setAthlete(athleteData);
        setError(null);
        toast.success(`Connected to Strava as ${athleteData?.firstname || 'athlete'}!`);
      }
      // Also handle legacy token format for backwards compatibility
      if (event.data.type === 'strava_token') {
        // This is the old format - we should not receive this anymore
        console.warn('Received legacy strava_token message. Please update backend.');
      }
    };

    window.addEventListener('message', handleMessage);
    validateSession();

    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, []);

  // Fetch activities from database (already imported)
  const fetchStoredActivities = async (token) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/strava/activities/stored`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setActivities(response.data.activities || []);
    } catch (err) {
      console.log('Failed to fetch stored activities:', err);
    }
  };

  // Handle Strava authentication
  const handleAuth = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_BASE_URL}/strava/auth`);
      // Redirect to Strava OAuth
      window.location.href = response.data.auth_url;
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Failed to initiate Strava authentication';
      setError(errorMsg);
      toast.error(errorMsg);
      setLoading(false);
    }
  };

  // Fetch and import activities from Strava API
  const handleFetchActivities = async () => {
    if (!sessionToken) {
      setError('Please authenticate with Strava first');
      toast.warning('Please connect to Strava first');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_BASE_URL}/strava/activities`, {
        headers: getAuthHeader()
      });
      const fetchedActivities = response.data.activities || [];
      setActivities(fetchedActivities);
      toast.success(`Loaded ${fetchedActivities.length} activities from Strava`);
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Failed to fetch activities';
      setError(errorMsg);
      toast.error(errorMsg);

      // If session expired, clear it
      if (err.response?.status === 401) {
        handleLogout();
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      await axios.post(`${API_BASE_URL}/strava/logout`, {}, {
        headers: getAuthHeader()
      });
      toast.info('Disconnected from Strava');
    } catch (err) {
      console.log('Logout error:', err);
    }

    // Clear local state
    localStorage.removeItem('strava_session_token');
    setSessionToken(null);
    setAthlete(null);
    setActivities([]);
    setError(null);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatPace = (speedKmh) => {
    if (!speedKmh || speedKmh === 0) return 'N/A';
    const paceMinPerKm = 60 / speedKmh;
    const minutes = Math.floor(paceMinPerKm);
    const seconds = Math.round((paceMinPerKm - minutes) * 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}/km`;
  };

  // Show loading while validating session
  if (validating) {
    return (
      <div className="strava-import">
        <h2>Import Strava Activities</h2>
        <p className="description">Checking connection status...</p>
      </div>
    );
  }

  return (
    <div className="strava-import">
      <h2>Import Strava Activities</h2>
      <p className="description">
        Connect your Strava account to import and view your training activities.
        Your activities are securely stored on the server.
      </p>

      {!sessionToken && (
        <div className="auth-section">
          <button
            onClick={handleAuth}
            disabled={loading}
            className="auth-button"
          >
            {loading ? 'Connecting...' : 'Connect to Strava'}
          </button>
        </div>
      )}

      {sessionToken && (
        <div className="authenticated-section">
          <div className="status-badge">
            Connected as {athlete?.firstname} {athlete?.lastname}
          </div>
          <div className="button-group">
            <button
              onClick={handleFetchActivities}
              disabled={loading}
              className="fetch-button"
            >
              {loading ? 'Loading...' : 'Fetch Latest Activities'}
            </button>
            <button
              onClick={handleLogout}
              className="logout-button"
            >
              Disconnect
            </button>
          </div>
        </div>
      )}

      {error && (
        <ErrorAlert
          message={error}
          onRetry={sessionToken ? handleFetchActivities : handleAuth}
          onDismiss={() => setError(null)}
        />
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
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {activities.map((activity) => (
                  <tr key={activity.id}>
                    <td>{formatDate(activity.start_date)}</td>
                    <td className="activity-name">{activity.name}</td>
                    <td>{activity.activity_type}</td>
                    <td>{activity.distance_km?.toFixed(2) || '0.00'} km</td>
                    <td>{Math.round(activity.moving_time_minutes || 0)} min</td>
                    <td>{formatPace(activity.average_speed_kmh)}</td>
                    <td>{activity.average_heartrate ? `${Math.round(activity.average_heartrate)} bpm` : 'N/A'}</td>
                    <td>
                      {activity.linked_workout_id ? (
                        <span className="linked-badge">Linked</span>
                      ) : (
                        <span className="unlinked-badge">Unlinked</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activities.length === 0 && sessionToken && !loading && (
        <div className="empty-state">
          <p>No activities loaded yet. Click "Fetch Latest Activities" to import your Strava data.</p>
        </div>
      )}
    </div>
  )
}

export default StravaImport
