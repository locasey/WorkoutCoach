/**
 * Phase Calculator
 *
 * Calculates default phase distributions for periodized training blocks.
 * Phases: Base (~25%), Build (~40%), Peak (~20%), Taper (~15%)
 *
 * @see docs/ARCHITECTURE_ROADMAP.md for phase distribution rationale
 */

/**
 * Calculate default phase map from total weeks.
 *
 * Distribution rationale (Lydiard/Daniels-inspired):
 * - Base: ~25% — aerobic foundation
 * - Build: ~40% — threshold & tempo development
 * - Peak: ~20% — race-specific sharpening
 * - Taper: ~15% — volume reduction, freshness
 *
 * Short plans (<8 weeks) use a minimum viable distribution.
 *
 * @param {number} totalWeeks - Total training weeks (4–52)
 * @returns {{ base: number[], build: number[], peak: number[], taper: number[] }}
 */
export function calculatePhaseMap(totalWeeks) {
  if (totalWeeks < 4) totalWeeks = 4
  if (totalWeeks > 52) totalWeeks = 52

  let taperWeeks, peakWeeks, buildWeeks, baseWeeks

  if (totalWeeks < 8) {
    // Short plans: minimal viable phases
    taperWeeks = 1
    peakWeeks = 1
    baseWeeks = 2
    buildWeeks = totalWeeks - taperWeeks - peakWeeks - baseWeeks
  } else {
    // Standard distribution
    taperWeeks = Math.min(3, Math.max(2, Math.floor(totalWeeks * 0.15)))
    const remaining1 = totalWeeks - taperWeeks
    peakWeeks = Math.max(2, Math.floor(remaining1 * 0.20))
    const remaining2 = remaining1 - peakWeeks
    buildWeeks = Math.max(3, Math.floor(remaining2 * 0.60))
    baseWeeks = remaining2 - buildWeeks
  }

  // Build week number arrays
  let weekCounter = 1
  const base = Array.from({ length: baseWeeks }, () => weekCounter++)
  const build = Array.from({ length: buildWeeks }, () => weekCounter++)
  const peak = Array.from({ length: peakWeeks }, () => weekCounter++)
  const taper = Array.from({ length: taperWeeks }, () => weekCounter++)

  return { base, build, peak, taper }
}

/**
 * Adjust a phase map while keeping total weeks constant.
 *
 * @param {Object} currentMap - Current phase map { base: [], build: [], peak: [], taper: [] }
 * @param {string} phaseName - Phase to adjust ("base", "build", "peak", "taper")
 * @param {number} delta - Change in weeks (+1 or -1)
 * @param {number} totalWeeks - Total weeks that must be maintained
 * @returns {Object|null} Adjusted phase map, or null if adjustment is invalid
 */
export function adjustPhaseMap(currentMap, phaseName, delta, totalWeeks) {
  const phases = ['base', 'build', 'peak', 'taper']
  const counts = {}
  phases.forEach((p) => {
    counts[p] = currentMap[p]?.length || 0
  })

  const newCount = counts[phaseName] + delta
  if (newCount < 1) return null // Every phase needs at least 1 week

  // Find a phase to take from / give to (prefer adjacent phases)
  const phaseIndex = phases.indexOf(phaseName)
  const adjacentOrder = []
  // Check neighbors first, then further phases
  if (phaseIndex > 0) adjacentOrder.push(phases[phaseIndex - 1])
  if (phaseIndex < phases.length - 1) adjacentOrder.push(phases[phaseIndex + 1])
  phases.forEach((p) => {
    if (p !== phaseName && !adjacentOrder.includes(p)) adjacentOrder.push(p)
  })

  let compensatePhase = null
  for (const adj of adjacentOrder) {
    const adjNewCount = counts[adj] - delta
    if (adjNewCount >= 1) {
      compensatePhase = adj
      break
    }
  }

  if (!compensatePhase) return null

  counts[phaseName] = newCount
  counts[compensatePhase] = counts[compensatePhase] - delta

  // Rebuild week arrays
  let weekCounter = 1
  const result = {}
  phases.forEach((p) => {
    result[p] = Array.from({ length: counts[p] }, () => weekCounter++)
  })

  return result
}

/**
 * Get phase display info (name, color, focus).
 */
export const PHASE_INFO = {
  base: {
    label: 'Base',
    color: '#22c55e', // green
    focus: 'Aerobic base building, easy runs, building mileage',
  },
  build: {
    label: 'Build',
    color: '#f59e0b', // amber
    focus: 'Tempo and threshold work, increasing intensity',
  },
  peak: {
    label: 'Peak',
    color: '#ef4444', // red
    focus: 'Race-specific workouts, sharpening',
  },
  taper: {
    label: 'Taper',
    color: '#8b5cf6', // purple
    focus: 'Reduced volume, maintaining intensity, rest',
  },
}

/**
 * Calculate total weeks from today to a target date.
 * @param {string} targetDate - ISO date string (YYYY-MM-DD)
 * @returns {number} Number of full weeks
 */
export function calculateTotalWeeks(targetDate) {
  const target = new Date(targetDate)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  target.setHours(0, 0, 0, 0)
  const diffMs = target.getTime() - today.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  return Math.floor(diffDays / 7)
}
