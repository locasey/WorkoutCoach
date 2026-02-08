import React, { useState, useMemo } from 'react'
import { ChevronLeft, Minus, Plus } from 'lucide-react'
import { PHASE_INFO, adjustPhaseMap } from '../../utils/phaseCalculator'

const PHASE_ORDER = ['base', 'build', 'peak', 'taper']

/**
 * PhasePreview - Step 3 of GoalSetup wizard
 *
 * Displays a visual timeline of phases with colored bars and week counts.
 * Allows inline +/- adjustment with constraint: sum must equal total_weeks.
 */
export function PhasePreview({ phaseMap, totalWeeks, onBack, onGenerate, isGenerating }) {
  const [adjustedMap, setAdjustedMap] = useState(phaseMap)
  const [showAdjust, setShowAdjust] = useState(false)

  const handleAdjust = (phaseName, delta) => {
    const result = adjustPhaseMap(adjustedMap, phaseName, delta, totalWeeks)
    if (result) {
      setAdjustedMap(result)
    }
  }

  // Calculate widths as percentages
  const phaseWidths = useMemo(() => {
    const widths = {}
    PHASE_ORDER.forEach((p) => {
      const count = adjustedMap[p]?.length || 0
      widths[p] = (count / totalWeeks) * 100
    })
    return widths
  }, [adjustedMap, totalWeeks])

  return (
    <div className="goal-setup__step">
      <button className="goal-setup__back-btn" onClick={onBack} type="button">
        <ChevronLeft size={20} aria-hidden />
        Back
      </button>

      <h2 className="goal-setup__step-title">Your Training Plan</h2>
      <p className="goal-setup__step-desc">
        {totalWeeks} weeks of periodized training, broken into 4 phases.
      </p>

      {/* Phase Timeline Bar */}
      <div className="phase-preview__timeline" role="img" aria-label="Phase timeline">
        {PHASE_ORDER.map((phase) => {
          const info = PHASE_INFO[phase]
          const weeks = adjustedMap[phase]?.length || 0
          if (weeks === 0) return null
          return (
            <div
              key={phase}
              className="phase-preview__bar"
              style={{
                width: `${phaseWidths[phase]}%`,
                backgroundColor: info.color,
              }}
              title={`${info.label}: ${weeks} weeks`}
            >
              <span className="phase-preview__bar-label">
                {weeks >= 3 ? info.label : ''}
              </span>
            </div>
          )
        })}
      </div>

      {/* Phase Details */}
      <div className="phase-preview__phases">
        {PHASE_ORDER.map((phase) => {
          const info = PHASE_INFO[phase]
          const weeks = adjustedMap[phase] || []
          if (weeks.length === 0) return null

          const weekRange = `Wk ${weeks[0]}–${weeks[weeks.length - 1]}`

          return (
            <div key={phase} className="phase-preview__phase">
              <div className="phase-preview__phase-header">
                <div
                  className="phase-preview__phase-dot"
                  style={{ backgroundColor: info.color }}
                />
                <div className="phase-preview__phase-info">
                  <span className="phase-preview__phase-name">{info.label}</span>
                  <span className="phase-preview__phase-weeks">
                    {weeks.length} {weeks.length === 1 ? 'week' : 'weeks'} ({weekRange})
                  </span>
                </div>

                {showAdjust && (
                  <div className="phase-preview__adjust-controls">
                    <button
                      className="phase-preview__adjust-btn"
                      onClick={() => handleAdjust(phase, -1)}
                      disabled={weeks.length <= 1 || isGenerating}
                      aria-label={`Remove a week from ${info.label}`}
                      type="button"
                    >
                      <Minus size={14} />
                    </button>
                    <span className="phase-preview__adjust-count">{weeks.length}</span>
                    <button
                      className="phase-preview__adjust-btn"
                      onClick={() => handleAdjust(phase, 1)}
                      disabled={isGenerating}
                      aria-label={`Add a week to ${info.label}`}
                      type="button"
                    >
                      <Plus size={14} />
                    </button>
                  </div>
                )}
              </div>
              <p className="phase-preview__phase-focus">{info.focus}</p>
            </div>
          )
        })}
      </div>

      {/* Adjust toggle */}
      {!isGenerating && (
        <button
          className="goal-setup__text-btn"
          onClick={() => setShowAdjust(!showAdjust)}
          type="button"
        >
          {showAdjust ? 'Done Adjusting' : 'Adjust Phases'}
        </button>
      )}

      {/* Generate Button */}
      <button
        className="goal-setup__generate-btn"
        onClick={() => onGenerate(adjustedMap)}
        disabled={isGenerating}
      >
        {isGenerating ? (
          <>
            <span className="goal-setup__generate-spinner" />
            Generating Your Plan...
          </>
        ) : (
          'Generate Training Plan'
        )}
      </button>
    </div>
  )
}
