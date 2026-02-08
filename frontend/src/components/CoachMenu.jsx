import React from 'react'
import { RefreshCw, Plus, SlidersHorizontal, X } from 'lucide-react'
import './CoachMenu.css'

export function CoachMenu({ isOpen, onClose, onRegenerate, onNewBlock, onAdjustPhases }) {
  if (!isOpen) return null

  return (
    <div className="coach-menu__overlay" onClick={onClose}>
      <div className="coach-menu" onClick={(e) => e.stopPropagation()}>
        <div className="coach-menu__header">
          <h2 className="coach-menu__title">Coach</h2>
          <button className="coach-menu__close" onClick={onClose} aria-label="Close">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="coach-menu__actions">
          <button className="coach-menu__action" onClick={onRegenerate}>
            <RefreshCw className="coach-menu__action-icon" />
            <div className="coach-menu__action-text">
              <span className="coach-menu__action-label">Regenerate Current Week</span>
              <span className="coach-menu__action-desc">Get fresh workouts from your coach</span>
            </div>
          </button>

          <button className="coach-menu__action" onClick={onNewBlock}>
            <Plus className="coach-menu__action-icon" />
            <div className="coach-menu__action-text">
              <span className="coach-menu__action-label">Start New Training Block</span>
              <span className="coach-menu__action-desc">Set a new goal and training plan</span>
            </div>
          </button>

          <button className="coach-menu__action" onClick={onAdjustPhases}>
            <SlidersHorizontal className="coach-menu__action-icon" />
            <div className="coach-menu__action-text">
              <span className="coach-menu__action-label">Adjust Phase Timeline</span>
              <span className="coach-menu__action-desc">View and modify your training phases</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  )
}

export default CoachMenu
