import React, { useState, useEffect, useCallback } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { X } from 'lucide-react'

import { ModeSelect } from './ModeSelect'
import { RaceDetails } from './RaceDetails'
import { PhasePreview } from './PhasePreview'
import { MaintenanceDetails } from './MaintenanceDetails'
import { calculatePhaseMap } from '../../utils/phaseCalculator'
import { API_ROUTES } from '../../api/routes'
import { queryKeys } from '../../api/queryClient'
import { useToast } from '../Toast'

// useToast() returns { success, error, warning, info } convenience methods

import './GoalSetup.css'

/**
 * GoalSetup - Modal wizard for creating a new training block.
 *
 * Steps (training):
 *   1. ModeSelect - Training vs Maintenance
 *   2. RaceDetails - Event name, distance, date, experience
 *   3. PhasePreview - Visual timeline with adjustment
 *
 * Steps (maintenance):
 *   1. ModeSelect - Training vs Maintenance
 *   2. MaintenanceDetails - Available days, experience level (pre-filled from preferences)
 *
 * @param {Object} props
 * @param {boolean} props.isOpen - Whether modal is visible
 * @param {Function} props.onClose - Close modal callback
 */
export function GoalSetup({ isOpen, onClose }) {
  const queryClient = useQueryClient()
  const toast = useToast()

  const [step, setStep] = useState('mode') // mode | details | preview | maintenance
  const [raceData, setRaceData] = useState(null)
  const [phaseMap, setPhaseMap] = useState(null)

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setStep('mode')
      setRaceData(null)
      setPhaseMap(null)
    }
  }, [isOpen])

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return
    const handleKeyDown = (e) => {
      if (
        e.key === 'Escape' &&
        !createBlockMutation.isPending &&
        !generateWorkoutsMutation.isPending &&
        !updatePreferencesMutation.isPending &&
        !generateMaintenanceMutation.isPending
      ) {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  /**
   * Create training block mutation
   */
  const createBlockMutation = useMutation({
    mutationFn: async (blockData) => {
      const response = await axios.post(API_ROUTES.TRAINING_BLOCK.CREATE, blockData)
      return response.data
    },
  })

  /**
   * Generate workouts mutation
   */
  const generateWorkoutsMutation = useMutation({
    mutationFn: async ({ blockId, experienceLevel }) => {
      const response = await axios.post(
        API_ROUTES.TRAINING_BLOCK.GENERATE_WORKOUTS(blockId),
        { experience_level: experienceLevel }
      )
      return response.data
    },
  })

  /**
   * Maintenance mode: save preferences, then generate the first week
   */
  const updatePreferencesMutation = useMutation({
    mutationFn: async (prefs) => {
      const response = await axios.put(API_ROUTES.USER.PREFERENCES, prefs)
      return response.data
    },
  })

  const generateMaintenanceMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.post(API_ROUTES.WEEK.REGENERATE, {
        week_offset: 0,
        reason: 'Initial maintenance week',
      })
      return response.data
    },
  })

  const isGenerating =
    createBlockMutation.isPending ||
    generateWorkoutsMutation.isPending ||
    updatePreferencesMutation.isPending ||
    generateMaintenanceMutation.isPending

  /**
   * Maintenance mode has no goal data to collect up front — advance to the
   * MaintenanceDetails step (days/week, experience level) instead of closing.
   */
  const handleMaintenance = useCallback(() => {
    setStep('maintenance')
  }, [])

  /**
   * Handle maintenance details submission
   * 1. PUT save available_days/experience_level to account preferences
   * 2. POST generate the first maintenance week
   * 3. Invalidate queries and close
   */
  const handleMaintenanceDetails = useCallback(async (data) => {
    try {
      await updatePreferencesMutation.mutateAsync(data)
      await generateMaintenanceMutation.mutateAsync()

      queryClient.invalidateQueries({ queryKey: queryKeys.week.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.user.profile })

      toast.success('Your maintenance week is ready!')

      onClose()
    } catch (err) {
      const msg = err?.response?.data?.error || err.message || 'Failed to generate maintenance week'
      toast.error(msg)
    }
  }, [updatePreferencesMutation, generateMaintenanceMutation, queryClient, toast, onClose])

  /**
   * Handle race details submission
   */
  const handleRaceDetails = useCallback((data) => {
    setRaceData(data)
    const map = calculatePhaseMap(data.totalWeeks)
    setPhaseMap(map)
    setStep('preview')
  }, [])

  /**
   * Handle plan generation
   * 1. POST create block
   * 2. POST generate workouts
   * 3. Invalidate queries and close
   */
  const handleGenerate = useCallback(async (finalPhaseMap) => {
    try {
      // Step 1: Create training block
      const blockResult = await createBlockMutation.mutateAsync({
        event_name: raceData.eventName,
        event_distance: raceData.distance,
        target_date: raceData.targetDate,
        start_date: raceData.startDate,
        total_weeks: raceData.totalWeeks,
        phase_map: finalPhaseMap,
      })

      const blockId = blockResult.block.id

      // Step 2: Generate workouts
      await generateWorkoutsMutation.mutateAsync({
        blockId,
        experienceLevel: raceData.experience,
      })

      // Step 3: Invalidate queries and close
      queryClient.invalidateQueries({ queryKey: queryKeys.week.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.trainingBlock.all })

      toast.success(`Training plan created for ${raceData.eventName}!`)

      onClose()
    } catch (err) {
      const msg = err?.response?.data?.error || err.message || 'Failed to generate plan'
      toast.error(msg)
    }
  }, [raceData, createBlockMutation, generateWorkoutsMutation, queryClient, toast, onClose])

  if (!isOpen) return null

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget && !isGenerating) {
      onClose()
    }
  }

  return (
    <div className="goal-setup__backdrop" onClick={handleBackdropClick}>
      <div
        className="goal-setup__container"
        role="dialog"
        aria-modal="true"
        aria-label="Goal Setup"
      >
        {/* Close button */}
        {!isGenerating && (
          <button
            className="goal-setup__close-btn"
            onClick={onClose}
            aria-label="Close"
            type="button"
          >
            <X size={20} />
          </button>
        )}

        {/* Step content */}
        {step === 'mode' && (
          <ModeSelect
            onSelectTraining={() => setStep('details')}
            onSelectMaintenance={handleMaintenance}
          />
        )}

        {step === 'details' && (
          <RaceDetails
            onNext={handleRaceDetails}
            onBack={() => setStep('mode')}
            initialData={raceData || {}}
          />
        )}

        {step === 'preview' && phaseMap && raceData && (
          <PhasePreview
            phaseMap={phaseMap}
            totalWeeks={raceData.totalWeeks}
            onBack={() => setStep('details')}
            onGenerate={handleGenerate}
            isGenerating={isGenerating}
          />
        )}

        {step === 'maintenance' && (
          <MaintenanceDetails
            onBack={() => setStep('mode')}
            onNext={handleMaintenanceDetails}
          />
        )}
      </div>
    </div>
  )
}
