import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { Target, Calendar, MapPin, Trophy } from 'lucide-react'

import { ConfirmModal } from '../ConfirmModal'
import { useToast } from '../Toast'
import { queryKeys } from '../../api/queryClient'
import { API_ROUTES } from '../../api/routes'

import './BlockOverview.css'

/**
 * BlockOverview - Training block overview for the Plans tab.
 *
 * Shows phase timeline, completion stats, and "End Training Block" action.
 * If no active block exists, shows empty state with CTA.
 *
 * @param {Object} props
 * @param {Function} [props.onStartTraining] - Open GoalSetup when no block exists
 */
export function BlockOverview({ onStartTraining }) {
  const queryClient = useQueryClient()
  const toast = useToast()
  const [showEndConfirm, setShowEndConfirm] = useState(false)

  // Fetch active training block
  const { data: blockData, isLoading: blockLoading } = useQuery({
    queryKey: queryKeys.trainingBlock.current,
    queryFn: async () => {
      const response = await axios.get(API_ROUTES.TRAINING_BLOCK.CURRENT)
      return response.data
    },
    staleTime: 60 * 1000,
  })

  const block = blockData?.block
  const hasBlock = !!block

  // Fetch overview data when block exists
  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: queryKeys.trainingBlock.overview,
    queryFn: async () => {
      const response = await axios.get(API_ROUTES.TRAINING_BLOCK.OVERVIEW(block.id))
      return response.data
    },
    enabled: hasBlock,
    staleTime: 60 * 1000,
  })

  // End training block mutation
  const endBlockMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.delete(API_ROUTES.TRAINING_BLOCK.DELETE(block.id), {
        data: { completed: false },
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.trainingBlock.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.week.all })
      setShowEndConfirm(false)
      toast.success('Training block ended')
    },
    onError: (err) => {
      toast.error(err.response?.data?.error || 'Failed to end training block')
    },
  })

  // Loading state
  if (blockLoading) {
    return (
      <div className="block-overview">
        <div className="block-overview__loading">
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  // Empty state - no active block
  if (!hasBlock) {
    return (
      <div className="block-overview">
        <div className="block-overview__empty">
          <Target className="block-overview__empty-icon" aria-hidden="true" />
          <h2>No active training block</h2>
          <p>Start a training block to get a personalized, periodized plan for your next race.</p>
          {onStartTraining && (
            <button className="block-overview__empty-cta" onClick={onStartTraining}>
              Start Training Block
            </button>
          )}
        </div>
      </div>
    )
  }

  const phases = overview?.phases || []
  const totalWeeks = block.total_weeks || 1
  const currentWeek = overview?.current_week
  const completionRate = overview?.completion_rate || 0

  return (
    <div className="block-overview">
      {/* Header */}
      <div className="block-overview__header">
        <h1 className="block-overview__event-name">{block.event_name}</h1>
        <div className="block-overview__meta">
          <span className="block-overview__meta-item">
            <MapPin className="w-4 h-4" aria-hidden />
            {block.event_distance}
          </span>
          <span className="block-overview__meta-item">
            <Calendar className="w-4 h-4" aria-hidden />
            {block.target_date && new Date(block.target_date + 'T00:00:00').toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
            })}
          </span>
          {block.weeks_until_race != null && (
            <span className="block-overview__meta-item">
              <Trophy className="w-4 h-4" aria-hidden />
              {block.weeks_until_race} weeks to go
            </span>
          )}
        </div>
      </div>

      {/* Phase Timeline */}
      <div className="block-overview__timeline">
        <div className="block-overview__timeline-label">Training Phases</div>
        <div className="block-overview__phases">
          {phases.map((phase) => (
            <div
              key={phase.name}
              className={`block-overview__phase-bar block-overview__phase-bar--${phase.name} block-overview__phase-bar--${phase.status}`}
              style={{ flex: phase.weeks.length }}
              title={`${phase.name}: weeks ${phase.weeks[0]}-${phase.weeks[phase.weeks.length - 1]}`}
            >
              {phase.weeks.length >= 2 && phase.name}
            </div>
          ))}
        </div>
        {currentWeek && (
          <div className="block-overview__week-marker">
            Week {currentWeek} of {totalWeeks}
          </div>
        )}
      </div>

      {/* Stats Grid */}
      {!overviewLoading && overview && (
        <>
          {/* Progress Bar */}
          <div className="block-overview__progress">
            <div className="block-overview__progress-bar-bg">
              <div
                className="block-overview__progress-bar-fill"
                style={{ width: `${Math.round(completionRate * 100)}%` }}
              />
            </div>
            <div className="block-overview__progress-label">
              {Math.round(completionRate * 100)}% complete
            </div>
          </div>

          <div className="block-overview__stats">
            <div className="block-overview__stat-card">
              <div className="block-overview__stat-value">
                {overview.completed_workouts}/{overview.total_workouts}
              </div>
              <div className="block-overview__stat-label">Workouts Done</div>
            </div>
            <div className="block-overview__stat-card">
              <div className="block-overview__stat-value">
                {overview.total_distance_km}
              </div>
              <div className="block-overview__stat-label">KM Completed</div>
            </div>
          </div>
        </>
      )}

      {/* End Training Block */}
      <button
        className="block-overview__end-btn"
        onClick={() => setShowEndConfirm(true)}
      >
        End Training Block
      </button>

      <ConfirmModal
        isOpen={showEndConfirm}
        title="End Training Block"
        message={`Are you sure you want to end your "${block.event_name}" training block? This cannot be undone.`}
        confirmLabel="End Block"
        cancelLabel="Keep Training"
        onConfirm={() => endBlockMutation.mutate()}
        onCancel={() => setShowEndConfirm(false)}
        variant="danger"
      />
    </div>
  )
}

export default BlockOverview
