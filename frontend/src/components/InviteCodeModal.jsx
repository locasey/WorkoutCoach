import React, { useState } from 'react'
import { Ticket, Loader2, AlertCircle, CheckCircle } from 'lucide-react'
import './InviteCodeModal.css'

/**
 * InviteCodeModal Component
 *
 * Modal for new users to enter their beta invite code and consent.
 *
 * Props:
 *   isOpen: boolean
 *   onClose: () => void
 *   onSubmit: (inviteCode: string) => Promise<void>
 */
function InviteCodeModal({ isOpen, onClose, onSubmit }) {
  const [inviteCode, setInviteCode] = useState('')
  const [consent, setConsent] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!inviteCode.trim() || !consent) return

    setError('')
    setLoading(true)

    try {
      await onSubmit(inviteCode.trim())
    } catch (err) {
      setError(err.message || 'Invalid or expired invite code')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="invite-overlay" onClick={onClose}>
      <div className="invite-modal" onClick={(e) => e.stopPropagation()}>
        <div className="invite-header">
          <Ticket className="w-6 h-6" />
          <h2>Welcome to the Beta</h2>
          <p>Enter your invite code to create an account</p>
        </div>

        <form onSubmit={handleSubmit} className="invite-form">
          {error && (
            <div className="invite-error" role="alert">
              <AlertCircle className="w-4 h-4" />
              <span>{error}</span>
            </div>
          )}

          <div className="invite-input-group">
            <label htmlFor="invite-code">Invite Code</label>
            <input
              id="invite-code"
              type="text"
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
              placeholder="Enter your invite code"
              required
              disabled={loading}
              autoFocus
              autoComplete="off"
            />
          </div>

          <label className="invite-consent">
            <input
              type="checkbox"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
              disabled={loading}
            />
            <span>
              I agree to participate in the Workout Coach beta and understand my data
              will be used to improve the product.
            </span>
          </label>

          <div className="invite-actions">
            <button
              type="button"
              className="invite-cancel"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="invite-submit"
              disabled={loading || !inviteCode.trim() || !consent}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Creating account...</span>
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4" />
                  <span>Create Account</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default InviteCodeModal
