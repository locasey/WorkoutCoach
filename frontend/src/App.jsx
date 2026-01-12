import React, { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import StravaImport from './components/StravaImport'
import { WeekAheadView } from './components/WeekAheadView'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('week')

  return (
    <div className="app">
      <header className="app-header">
        <h1>🏃 Workout Coach</h1>
        <p>Your AI-powered training companion</p>
      </header>

      <nav className="tab-navigation">
        <button
          className={activeTab === 'week' ? 'active' : ''}
          onClick={() => setActiveTab('week')}
        >
          📅 Your Week Ahead
        </button>
        <button
          className={activeTab === 'chat' ? 'active' : ''}
          onClick={() => setActiveTab('chat')}
        >
          💬 Generate Workout Plan
        </button>
        <button
          className={activeTab === 'strava' ? 'active' : ''}
          onClick={() => setActiveTab('strava')}
        >
          📊 Strava Import
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'week' && <WeekAheadView />}
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'strava' && <StravaImport />}
      </main>
    </div>
  )
}

export default App

