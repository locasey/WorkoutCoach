import React, { useState } from 'react'
import axios from 'axios'
import { useToast } from './Toast'
import './ChatInterface.css'

function ChatInterface() {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [workoutPlan, setWorkoutPlan] = useState(null)
  const [planId, setPlanId] = useState(null)
  const toast = useToast()

  const examplePrompts = [
    "Create a 12-week half marathon training plan",
    "I need a 8-week 5K training program for beginners",
    "Generate a 16-week marathon plan with 4 runs per week"
  ]

  const handleExampleClick = (exampleText) => {
    setMessage(exampleText)
    // Focus the input after setting the message
    setTimeout(() => {
      const input = document.querySelector('.chat-input')
      if (input) input.focus()
    }, 0)
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (!message.trim() || loading) return

    const userMessage = message.trim()
    setMessage('')
    setLoading(true)

    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])

    try {
      const response = await axios.post('/api/chat', {
        message: userMessage
      })

      const { plan_id, workout_plan } = response.data
      setWorkoutPlan(workout_plan)
      setPlanId(plan_id)

      // Add assistant response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `I've created a ${workout_plan.duration_weeks}-week workout plan for: ${workout_plan.goal}. You can view it below and export it to Excel!`
      }])
    } catch (error) {
      console.error('Error generating workout plan:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error.response?.data?.error || error.message}. Please try again.`
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    if (!planId) return

    try {
      const response = await axios.get(`/api/export/excel/${planId}`, {
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `workout_plan_${planId}.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.success('Workout plan exported successfully!')
    } catch (error) {
      console.error('Error exporting Excel:', error)
      toast.error('Failed to export Excel file. Please try again.')
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h2>Welcome to Workout Coach! 🏃</h2>
            <p>Ask me to create a workout plan. For example:</p>
            <ul>
              {examplePrompts.map((prompt, idx) => (
                <li 
                  key={idx}
                  onClick={() => handleExampleClick(prompt)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault()
                      handleExampleClick(prompt)
                    }
                  }}
                  tabIndex={0}
                  role="button"
                  aria-label={`Use example: ${prompt}`}
                >
                  {prompt}
                </li>
              ))}
            </ul>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
      </div>

      {workoutPlan && (
        <div className="workout-plan-preview">
          <div className="workout-plan-header">
            <h3>📋 Workout Plan Preview</h3>
            <button onClick={handleExport} className="export-button">
              📥 Export to Excel
            </button>
          </div>
          <div className="plan-info">
            <p><strong>Goal:</strong> {workoutPlan.goal}</p>
            <p><strong>Duration:</strong> {workoutPlan.duration_weeks} weeks</p>
            <p><strong>Total Workouts:</strong> {workoutPlan.workouts?.length || 0}</p>
          </div>
          <div className="workouts-list">
            <h4>Weekly Schedule:</h4>
            <div className="workouts-grid">
              {workoutPlan.workouts?.slice(0, 10).map((workout, idx) => (
                <div key={idx} className="workout-card">
                  <div className="workout-header">
                    <span className="week-badge">Week {workout.week}</span>
                    <span className="type-badge">{workout.type.replace('_', ' ')}</span>
                  </div>
                  <div className="workout-details">
                    {workout.distance_km && <p>Distance: {workout.distance_km} km</p>}
                    {workout.duration_minutes && <p>Duration: {workout.duration_minutes} min</p>}
                    {workout.pace && <p>Pace: {workout.pace}</p>}
                    {workout.notes && <p className="notes">{workout.notes}</p>}
                  </div>
                </div>
              ))}
            </div>
            {workoutPlan.workouts?.length > 10 && (
              <p className="more-workouts">
                ... and {workoutPlan.workouts.length - 10} more workouts. Export to Excel to see the full plan!
              </p>
            )}
          </div>
        </div>
      )}

      <form onSubmit={handleSend} className="chat-input-form">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask for a workout plan..."
          disabled={loading}
          className="chat-input"
        />
        <button type="submit" disabled={loading || !message.trim()} className="send-button">
          {loading ? '⏳' : '➤'}
        </button>
      </form>
    </div>
  )
}

export default ChatInterface

