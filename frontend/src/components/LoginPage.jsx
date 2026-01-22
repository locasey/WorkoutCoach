import React, { useState } from 'react'
import axios from 'axios'
import { Lock, User, Loader2, AlertCircle } from 'lucide-react'
import './LoginPage.css'

/**
 * LoginPage Component
 *
 * Simple login form for authentication.
 * Supports username/password login with session token storage.
 *
 * Props:
 *   onLogin: Callback function called with session token on successful login
 */
function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await axios.post('/api/auth/login', {
        username,
        password
      })

      const { session_token, auth_enabled } = response.data

      // If auth is not enabled, just proceed
      if (!auth_enabled) {
        onLogin(null)
        return
      }

      // Store session token in localStorage
      if (session_token) {
        localStorage.setItem('auth_session', session_token)
      }

      // Notify parent of successful login
      onLogin(session_token)
    } catch (err) {
      console.error('Login error:', err)
      if (err.response?.status === 401) {
        setError('Invalid username or password')
      } else {
        setError(err.response?.data?.error || 'Login failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>Workout Coach</h1>
          <p>Sign in to continue</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="login-error" role="alert">
              <AlertCircle className="w-4 h-4" />
              <span>{error}</span>
            </div>
          )}

          <div className="input-group">
            <label htmlFor="username" className="sr-only">Username</label>
            <User className="input-icon" />
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Username"
              required
              disabled={loading}
              autoComplete="username"
              autoFocus
            />
          </div>

          <div className="input-group">
            <label htmlFor="password" className="sr-only">Password</label>
            <Lock className="input-icon" />
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
              disabled={loading}
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="login-button"
            disabled={loading || !username || !password}
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Signing in...</span>
              </>
            ) : (
              <span>Sign In</span>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

export default LoginPage
