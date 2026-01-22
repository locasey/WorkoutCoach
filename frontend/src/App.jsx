import React, { useState, useEffect } from 'react'
import axios from 'axios'
import ChatInterface from './components/ChatInterface'
import StravaImport from './components/StravaImport'
import { WeekAheadView } from './components/WeekAheadView'
import { PlanManager } from './components/PlanManager/PlanManager'
import { ToastProvider } from './components/Toast'
import LoginPage from './components/LoginPage'
import { API_BASE_URL } from './config/api'
import { LayoutGrid, Calendar, MessageSquare, Activity, Settings, LogOut } from 'lucide-react'
import './App.css'

// Configure axios base URL for production
if (API_BASE_URL) {
  axios.defaults.baseURL = API_BASE_URL
}

/**
 * Configure axios to include auth session token in all requests
 */
const setupAxiosAuth = (token) => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete axios.defaults.headers.common['Authorization']
  }
}

function App() {
  const [activeTab, setActiveTab] = useState('week')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [authChecking, setAuthChecking] = useState(true)

  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = async () => {
      const storedToken = localStorage.getItem('auth_session')

      // Setup axios with stored token if available
      if (storedToken) {
        setupAxiosAuth(storedToken)
      }

      try {
        const response = await axios.get('/api/auth/check')
        const { authenticated, auth_enabled } = response.data

        // If auth is not enabled, user is always authenticated
        if (!auth_enabled) {
          setIsAuthenticated(true)
        } else {
          setIsAuthenticated(authenticated)
          // Clear stored token if session is invalid
          if (!authenticated && storedToken) {
            localStorage.removeItem('auth_session')
            setupAxiosAuth(null)
          }
        }
      } catch (err) {
        console.error('Auth check failed:', err)
        setIsAuthenticated(false)
        localStorage.removeItem('auth_session')
        setupAxiosAuth(null)
      } finally {
        setAuthChecking(false)
      }
    }

    checkAuth()
  }, [])

  // Handle successful login
  const handleLogin = (sessionToken) => {
    if (sessionToken) {
      localStorage.setItem('auth_session', sessionToken)
      setupAxiosAuth(sessionToken)
    }
    setIsAuthenticated(true)
  }

  // Handle logout
  const handleLogout = async () => {
    try {
      await axios.post('/api/auth/logout')
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      localStorage.removeItem('auth_session')
      setupAxiosAuth(null)
      setIsAuthenticated(false)
    }
  }

  // Show loading state while checking auth
  if (authChecking) {
    return (
      <div className="auth-loading">
        <div className="auth-loading-spinner" />
      </div>
    )
  }

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <LoginPage onLogin={handleLogin} />
  }

  return (
    <ToastProvider>
      <div className="app pb-20 md:pb-0">
        <header className="app-header hidden md:block">
          <div className="header-content">
            <div>
              <h1>Workout Coach</h1>
              <p>Your AI-powered training companion</p>
            </div>
            <button
              onClick={handleLogout}
              className="logout-button"
              aria-label="Sign out"
            >
              <LogOut className="w-5 h-5" />
              <span>Sign Out</span>
            </button>
          </div>
        </header>

        <main className="app-main" role="tabpanel" aria-labelledby={`tab-${activeTab}`}>
          {activeTab === 'week' && <WeekAheadView initialView="week" />}
          {activeTab === 'month' && <WeekAheadView initialView="month" />}
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'plans' && <PlanManager />}
          {activeTab === 'strava' && <StravaImport />}
        </main>

        <nav className="bottom-nav" role="tablist">
          <button
            id="tab-week"
            role="tab"
            aria-selected={activeTab === 'week'}
            className={activeTab === 'week' ? 'active' : ''}
            onClick={() => setActiveTab('week')}
          >
            <LayoutGrid className="w-6 h-6" />
            <span>Week</span>
          </button>
          <button
            id="tab-month"
            role="tab"
            aria-selected={activeTab === 'month'}
            className={activeTab === 'month' ? 'active' : ''}
            onClick={() => setActiveTab('month')}
          >
            <Calendar className="w-6 h-6" />
            <span>Month</span>
          </button>
          <button
            id="tab-chat"
            role="tab"
            aria-selected={activeTab === 'chat'}
            className={activeTab === 'chat' ? 'active' : ''}
            onClick={() => setActiveTab('chat')}
          >
            <MessageSquare className="w-6 h-6" />
            <span>Coach</span>
          </button>
          <button
            id="tab-strava"
            role="tab"
            aria-selected={activeTab === 'strava'}
            className={activeTab === 'strava' ? 'active' : ''}
            onClick={() => setActiveTab('strava')}
          >
            <Activity className="w-6 h-6" />
            <span>Strava</span>
          </button>
          <button
            id="tab-plans"
            role="tab"
            aria-selected={activeTab === 'plans'}
            className={activeTab === 'plans' ? 'active' : ''}
            onClick={() => setActiveTab('plans')}
          >
            <Settings className="w-6 h-6" />
            <span>Settings</span>
          </button>
        </nav>
      </div>
    </ToastProvider>
  )
}

export default App

