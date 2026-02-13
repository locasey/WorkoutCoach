import React, { useState } from 'react'
import axios from 'axios'
import { GoogleLogin } from '@react-oauth/google'
import { Loader2, AlertCircle } from 'lucide-react'
import InviteCodeModal from './InviteCodeModal'
import './GoogleLoginPage.css'

/**
 * GoogleLoginPage Component
 *
 * Google Sign-In page with invite code flow for new users.
 *
 * Flow:
 * 1. User clicks "Sign in with Google"
 * 2. Google returns credential (id_token)
 * 3. POST /api/auth/google { credential }
 * 4a. Existing user -> logged in
 * 4b. New user -> 403 INVITE_REQUIRED -> show InviteCodeModal
 * 5. InviteCodeModal: POST /api/auth/google { credential, invite_code, consent }
 *
 * Props:
 *   onLogin: (sessionToken, user) => void
 */
function GoogleLoginPage({ onLogin }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [pendingCredential, setPendingCredential] = useState(null)

  const handleGoogleSuccess = async (credentialResponse) => {
    setError('')
    setLoading(true)

    try {
      const response = await axios.post('/api/auth/google', {
        credential: credentialResponse.credential
      })

      const { session_token, user } = response.data
      onLogin(session_token, user)
    } catch (err) {
      if (err.response?.status === 403 && err.response?.data?.code === 'INVITE_REQUIRED') {
        // New user — save credential and show invite code modal
        setPendingCredential(credentialResponse.credential)
        setShowInviteModal(true)
      } else {
        setError(err.response?.data?.error || 'Sign in failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleError = () => {
    setError('Google Sign-In failed. Please try again.')
  }

  const handleInviteSubmit = async (inviteCode) => {
    setError('')
    setLoading(true)

    try {
      const response = await axios.post('/api/auth/google', {
        credential: pendingCredential,
        invite_code: inviteCode,
        consent: true
      })

      const { session_token, user } = response.data
      setShowInviteModal(false)
      onLogin(session_token, user)
    } catch (err) {
      setLoading(false)
      throw new Error(err.response?.data?.error || 'Failed to create account')
    }
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>Workout Coach</h1>
          <p>Plan your work(out), work your plan</p>
        </div>

        {error && (
          <div className="login-error" role="alert">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </div>
        )}

        <div className="google-login-wrapper">
          {loading ? (
            <div className="login-loading">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Signing in...</span>
            </div>
          ) : (
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              theme="outline"
              size="large"
              width="320"
              text="signin_with"
              shape="rectangular"
            />
          )}
        </div>

        <p className="login-footer">
          Beta access requires an invite code
        </p>
      </div>

      <InviteCodeModal
        isOpen={showInviteModal}
        onClose={() => {
          setShowInviteModal(false)
          setPendingCredential(null)
        }}
        onSubmit={handleInviteSubmit}
      />
    </div>
  )
}

export default GoogleLoginPage
