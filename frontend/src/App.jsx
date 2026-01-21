import React, { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import StravaImport from './components/StravaImport'
import { WeekAheadView } from './components/WeekAheadView'
import { PlanManager } from './components/PlanManager/PlanManager'
import { ToastProvider } from './components/Toast'
import { LayoutGrid, Calendar, MessageSquare, Activity, Settings } from 'lucide-react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('week')

  return (
    <ToastProvider>
      <div className="app pb-20 md:pb-0">
        <header className="app-header hidden md:block">
          <h1>🏃 Workout Coach</h1>
          <p>Your AI-powered training companion</p>
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

