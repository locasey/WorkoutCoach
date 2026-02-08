import React from 'react'
import { Target, Dumbbell } from 'lucide-react'

/**
 * ModeSelect - Step 1 of GoalSetup wizard
 *
 * Two cards: "Train for a Race" vs "Just Staying Fit"
 * "Just Staying Fit" closes modal (maintenance mode).
 */
export function ModeSelect({ onSelectTraining, onSelectMaintenance }) {
  return (
    <div className="goal-setup__step">
      <h2 className="goal-setup__step-title">What's your goal?</h2>
      <p className="goal-setup__step-desc">Choose how you want your coach to work with you.</p>

      <div className="goal-setup__mode-cards">
        <button
          className="goal-setup__mode-card goal-setup__mode-card--training"
          onClick={onSelectTraining}
        >
          <Target className="goal-setup__mode-icon" size={32} aria-hidden />
          <h3>Train for a Race</h3>
          <p>Periodized plan with accountability. Set a race goal and date, get a structured training block.</p>
        </button>

        <button
          className="goal-setup__mode-card goal-setup__mode-card--maintenance"
          onClick={onSelectMaintenance}
        >
          <Dumbbell className="goal-setup__mode-icon" size={32} aria-hidden />
          <h3>Just Staying Fit</h3>
          <p>Flexible weekly suggestions. No rigid commitment, just smart week-by-week guidance.</p>
        </button>
      </div>
    </div>
  )
}
