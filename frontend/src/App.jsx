import React, { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import StravaImport from './components/StravaImport'
import { WeekAheadView } from './components/WeekAheadView'
import { PlanManager } from './components/PlanManager/PlanManager'
import { ToastProvider } from './components/Toast'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('week')

  return (
    <ToastProvider>
    <div className="app">
      <header className="app-header">
        <h1>🏃 Workout Coach</h1>
        <p>Your AI-powered training companion</p>
      </header>

      <nav className="tab-navigation" role="tablist">
        <button
          id="tab-week"
          role="tab"
          aria-selected={activeTab === 'week'}
          aria-controls="panel-week"
          className={activeTab === 'week' ? 'active' : ''}
          onClick={() => setActiveTab('week')}
        >
          Your Week Ahead
        </button>
        <button
          id="tab-chat"
          role="tab"
          aria-selected={activeTab === 'chat'}
          aria-controls="panel-chat"
          className={activeTab === 'chat' ? 'active' : ''}
          onClick={() => setActiveTab('chat')}
        >
          Generate Workout Plan
        </button>
        <button
          id="tab-plans"
          role="tab"
          aria-selected={activeTab === 'plans'}
          aria-controls="panel-plans"
          className={activeTab === 'plans' ? 'active' : ''}
          onClick={() => setActiveTab('plans')}
        >
          My Plans
        </button>
        <button
          id="tab-strava"
          role="tab"
          aria-selected={activeTab === 'strava'}
          aria-controls="panel-strava"
          className={activeTab === 'strava' ? 'active' : ''}
          onClick={() => setActiveTab('strava')}
        >
          Strava Import
        </button>
      </nav>

      <main className="app-main" role="tabpanel" aria-labelledby={`tab-${activeTab}`}>
        {activeTab === 'week' && <WeekAheadView />}
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'plans' && <PlanManager />}
        {activeTab === 'strava' && <StravaImport />}
      </main>
    </div>
    </ToastProvider>
  )
}

export default App

