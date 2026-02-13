import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useQuery } from '@tanstack/react-query'
import { GoogleOAuthProvider } from '@react-oauth/google'
import { WeekView } from './components/WeekView'
import { BlockOverview } from './components/BlockOverview'
import { GoalSetup } from './components/GoalSetup'
import { CoachMenu } from './components/CoachMenu'
import { ToastProvider } from './components/Toast'
import GoogleLoginPage from './components/GoogleLoginPage'
import { API_BASE_URL } from './config/api'
import { queryKeys } from './api/queryClient'
import { API_ROUTES } from './api/routes'
import { LayoutGrid, Activity, ClipboardList, Target, User } from 'lucide-react'
import ProfilePage from './components/ProfilePage'
import './App.css'

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

// Feature flags - Strava integration disabled by default (LOC-23)
const STRAVA_ENABLED = import.meta.env.VITE_STRAVA_ENABLED === 'true'

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
  const [showGoalSetup, setShowGoalSetup] = useState(false)
  const [showRegenerate, setShowRegenerate] = useState(false)
  const [showCoachMenu, setShowCoachMenu] = useState(false)
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
        const { authenticated } = response.data
        setIsAuthenticated(authenticated)
        if (!authenticated && storedToken) {
          localStorage.removeItem('auth_session')
          setupAxiosAuth(null)
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

  // Redirect to 'week' if Strava tab selected but feature disabled (LOC-23)
  useEffect(() => {
    if (!STRAVA_ENABLED && activeTab === 'strava') {
      setActiveTab('week')
    }
  }, [activeTab])

  // Query active training block for Coach tab state-awareness
  const { data: blockData } = useQuery({
    queryKey: queryKeys.trainingBlock.current,
    queryFn: async () => {
      const response = await axios.get(API_ROUTES.TRAINING_BLOCK.CURRENT)
      return response.data
    },
    staleTime: 60 * 1000,
    enabled: isAuthenticated,
  })
  const hasActiveBlock = !!blockData?.block

  /**
   * Coach tab: state-aware behavior
   * - No active block -> open GoalSetup
   * - Active block -> navigate to Week tab + open RegenerateModal
   */
  const handleCoachClick = () => {
    if (hasActiveBlock) {
      setShowCoachMenu(true)
    } else {
      setShowGoalSetup(true)
    }
  }

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
    return (
      <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
        <GoogleLoginPage onLogin={handleLogin} />
      </GoogleOAuthProvider>
    )
  }

  return (
    <ToastProvider>
      <div className="app pb-20 md:pb-0">
        <header className="app-header hidden md:block">
          <div className="header-content">
            <div>
              <h1>Workout Coach</h1>
              <p>Plan your work(out), work your plan</p>
            </div>
          </div>
          {/* Desktop nav: horizontal tabs below title; visible only at >=769px */}
          <nav className="desktop-nav hidden md:flex" role="tablist" aria-label="Main navigation">
            <button
              id="desktop-tab-week"
              role="tab"
              aria-selected={activeTab === 'week'}
              className={activeTab === 'week' ? 'active' : ''}
              onClick={() => setActiveTab('week')}
            >
              <LayoutGrid className="w-5 h-5" aria-hidden />
              <span>Week</span>
            </button>
            <button
              id="desktop-tab-coach"
              role="tab"
              aria-selected={false}
              className=""
              onClick={handleCoachClick}
            >
              <Target className="w-5 h-5" aria-hidden />
              <span>Coach</span>
            </button>
            {STRAVA_ENABLED && (
              <button
                id="desktop-tab-strava"
                role="tab"
                aria-selected={activeTab === 'strava'}
                className={activeTab === 'strava' ? 'active' : ''}
                onClick={() => setActiveTab('strava')}
              >
                <Activity className="w-5 h-5" aria-hidden />
                <span>Strava</span>
              </button>
            )}
            <button
              id="desktop-tab-plans"
              role="tab"
              aria-selected={activeTab === 'plans'}
              className={activeTab === 'plans' ? 'active' : ''}
              onClick={() => setActiveTab('plans')}
            >
              <ClipboardList className="w-5 h-5" aria-hidden />
              <span>Plans</span>
            </button>
            <button
              id="desktop-tab-profile"
              role="tab"
              aria-selected={activeTab === 'profile'}
              className={activeTab === 'profile' ? 'active' : ''}
              onClick={() => setActiveTab('profile')}
            >
              <User className="w-5 h-5" aria-hidden />
              <span>Profile</span>
            </button>
          </nav>
        </header>

        <main className="app-main" role="tabpanel" aria-labelledby={`tab-${activeTab}`}>
          {activeTab === 'week' && (
            <WeekView
              onStartTraining={() => setShowGoalSetup(true)}
              showRegenerate={showRegenerate}
              setShowRegenerate={setShowRegenerate}
            />
          )}
          {activeTab === 'plans' && (
            <BlockOverview onStartTraining={() => setShowGoalSetup(true)} />
          )}
          {activeTab === 'profile' && (
            <ProfilePage onLogout={handleLogout} />
          )}
        </main>

        {/* Goal Setup Modal */}
        <GoalSetup
          isOpen={showGoalSetup}
          onClose={() => setShowGoalSetup(false)}
        />

        {/* Coach Menu (active block) */}
        <CoachMenu
          isOpen={showCoachMenu}
          onClose={() => setShowCoachMenu(false)}
          onRegenerate={() => {
            setShowCoachMenu(false)
            setActiveTab('week')
            setShowRegenerate(true)
          }}
          onNewBlock={() => {
            setShowCoachMenu(false)
            setShowGoalSetup(true)
          }}
          onAdjustPhases={() => {
            setShowCoachMenu(false)
            setActiveTab('plans')
          }}
        />

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
            id="tab-coach"
            role="tab"
            aria-selected={false}
            className=""
            onClick={handleCoachClick}
          >
            <Target className="w-6 h-6" />
            <span>Coach</span>
          </button>
          {STRAVA_ENABLED && (
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
          )}
          <button
            id="tab-plans"
            role="tab"
            aria-selected={activeTab === 'plans'}
            className={activeTab === 'plans' ? 'active' : ''}
            onClick={() => setActiveTab('plans')}
          >
            <ClipboardList className="w-6 h-6" />
            <span>Plans</span>
          </button>
          <button
            id="tab-profile"
            role="tab"
            aria-selected={activeTab === 'profile'}
            className={activeTab === 'profile' ? 'active' : ''}
            onClick={() => setActiveTab('profile')}
          >
            <User className="w-6 h-6" />
            <span>Profile</span>
          </button>
        </nav>
      </div>
    </ToastProvider>
  )
}

export default App
