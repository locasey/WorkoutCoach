import React, { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import StravaImport from './components/StravaImport'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('chat')

  return (
    <div className="app">
      <header className="app-header">
        <h1>🏃 Workout Coach</h1>
        <p>Your AI-powered training companion</p>
      </header>

      <nav className="tab-navigation">
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
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'strava' && <StravaImport />}
      </main>
    </div>
  )
}

export default App

