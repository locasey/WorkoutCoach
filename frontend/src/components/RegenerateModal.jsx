import React, { useState, useEffect } from 'react'
import { RefreshCw } from 'lucide-react'
import './RegenerateModal.css'

/**
 * RegenerateModal - Coach-style warning modal before regenerating a week.
 *
 * Shows coach messaging, optional reason textarea, and confirm/cancel buttons.
 * Follows ConfirmModal patterns: backdrop click to close, Escape key, z-index 2000.
 *
 * @param {Object} props
 * @param {boolean} props.isOpen - Whether modal is visible
 * @param {Function} props.onClose - Close without regenerating
 * @param {Function} props.onConfirm - Called with (reason) string when user confirms
 * @param {boolean} props.isRegenerating - Show spinner on confirm button
 * @param {number} [props.weekNumber] - Current week number in the block
 * @param {string} [props.phase] - Current phase name (base, build, peak, taper)
 */
export function RegenerateModal({
  isOpen,
  onClose,
  onConfirm,
  isRegenerating = false,
  weekNumber,
  phase,
}) {
  const [reason, setReason] = useState('')

  // Reset reason when modal opens
  useEffect(() => {
    if (isOpen) setReason('')
  }, [isOpen])

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && !isRegenerating) onClose?.()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, isRegenerating, onClose])

  if (!isOpen) return null

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget && !isRegenerating) onClose?.()
  }

  const handleConfirm = () => {
    onConfirm?.(reason.trim())
  }

  const weekLabel = weekNumber ? `Week ${weekNumber}` : 'this week'

  return (
    <div className="regenerate-modal-backdrop" onClick={handleBackdropClick}>
      <div
        className="regenerate-modal-container"
        role="dialog"
        aria-modal="true"
        aria-labelledby="regenerate-modal-title"
      >
        <div className="regenerate-modal-header">
          <RefreshCw className="regenerate-modal-icon" aria-hidden="true" />
          <h2 id="regenerate-modal-title" className="regenerate-modal-title">
            Regenerate {weekLabel}
          </h2>
        </div>

        <div className="regenerate-modal-body">
          <p className="regenerate-modal-message">
            Your coach will create a fresh set of workouts for {weekLabel}
            {phase && (
              <>
                {' '}
                (<span className="regenerate-modal-phase">{phase}</span> phase)
              </>
            )}
            . Your current workouts will be saved — you can revert if you change
            your mind.
          </p>

          <label className="regenerate-modal-label" htmlFor="regenerate-reason">
            Tell your coach why (optional)
          </label>
          <textarea
            id="regenerate-reason"
            className="regenerate-modal-textarea"
            placeholder="e.g., I'm feeling tired, legs are sore..."
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            disabled={isRegenerating}
            maxLength={500}
          />
        </div>

        <div className="regenerate-modal-footer">
          <button
            type="button"
            className="regenerate-modal-btn regenerate-modal-btn--secondary"
            onClick={onClose}
            disabled={isRegenerating}
          >
            Cancel
          </button>
          <button
            type="button"
            className="regenerate-modal-btn regenerate-modal-btn--primary"
            onClick={handleConfirm}
            disabled={isRegenerating}
          >
            {isRegenerating ? (
              <>
                <span className="regenerate-modal-spinner" />
                Regenerating...
              </>
            ) : (
              'Regenerate Week'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default RegenerateModal
