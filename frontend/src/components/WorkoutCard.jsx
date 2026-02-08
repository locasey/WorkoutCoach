import React, { useState, useEffect } from 'react';
import { Check, Minus, Edit2, Clock, Gauge, Heart, StickyNote, ChevronDown, ChevronUp, Calendar, Zap } from 'lucide-react';
import confetti from 'canvas-confetti';
import './WorkoutCard.css';

/**
 * WorkoutCard Component
 *
 * @param {Object} workout - Workout data from mapWorkoutToDesign
 * @param {Function} onToggle - Callback to toggle completion status
 * @param {Function} onEdit - Callback to open edit modal
 * @param {boolean} isToday - Whether this workout is for today
 * @param {boolean} isAM - LOC-22: Whether this is the AM/first slot in a multi-workout day
 * @param {boolean} isPM - LOC-22: Whether this is the PM/second slot in a multi-workout day
 * @param {string} [phase] - Training phase ('base', 'build', 'peak', 'taper') - Phase 3
 * @param {Object} [actuals] - Actual workout data (distance, duration, pace) - Phase 3
 */
export function WorkoutCard({ workout, onToggle, onEdit, isToday = false, isAM = false, isPM = false, phase, actuals }) {
  const [justCompleted, setJustCompleted] = useState(false);

  // Track when workout status changes to completed
  useEffect(() => {
    if (workout.status === 'completed') {
      setJustCompleted(true);
      
      // Trigger confetti celebration
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.8 },
        colors: ['#8eb19d', '#072ac8', '#eacdc2']
      });

      // Reset animation state after it completes
      const timer = setTimeout(() => setJustCompleted(false), 400);
      return () => clearTimeout(timer);
    }
  }, [workout.status]);

  const isEmpty = !workout.type || workout.id?.startsWith('placeholder-');
  
  // Extract duration value and unit
  const durationMatch = workout.duration?.match(/(\d+)\s*(.*)/);
  const durationValue = durationMatch ? durationMatch[1] : '';
  const durationUnit = durationMatch ? durationMatch[2] : '';

  return (
    <div className={`workout-card ${isToday ? 'today' : ''} ${workout.status === 'completed' ? 'completed' : ''} ${workout.status === 'rest' ? 'rest' : ''} ${isEmpty ? 'empty' : ''}`}>
      <div className="card-header">
        <span className="card-day">
          {workout.day}
          {/* LOC-22: Show AM/PM indicator for multi-workout days */}
          {(isAM || isPM) && (
            <span className="ml-1 text-[10px] font-normal text-gray-500">
              {isAM ? 'AM' : 'PM'}
            </span>
          )}
        </span>
        {isToday && (
          <div className="flex items-center gap-1 text-[10px] font-bold text-persian-blue uppercase">
            <Calendar className="w-3 h-3" />
            Today
          </div>
        )}
        {/* Phase badge for training mode - Phase 3 */}
        {(phase || workout.phase) && (
          <span className="phase-badge" data-phase={phase || workout.phase}>
            {(phase || workout.phase).charAt(0).toUpperCase() + (phase || workout.phase).slice(1)}
          </span>
        )}
      </div>

      {!isEmpty ? (
        <>
          <div className="card-title">{workout.status === 'rest' ? 'Rest Day' : workout.type}</div>
          
          {workout.status !== 'rest' && (
            <div className="card-duration">
              {durationValue || '--'}
              <span className="duration-unit">{durationUnit || 'min'}</span>
            </div>
          )}

          <div className="side-by-side">
            <div className="metrics-group">
              <div className="metrics-label">Planned</div>
              <div className="metrics-row">
                <span className="planned-value">{workout.distance || '--'}</span>
              </div>
            </div>
            <div className="metrics-group">
              <div className="metrics-label">Actual</div>
              <div className="metrics-row">
                {/* Phase 3: Show actuals when available */}
                <span className={`actual-value ${(actuals?.distance || workout.actuals?.distance) ? 'active' : ''}`}>
                  {actuals?.distance || workout.actuals?.distance || '--'}
                </span>
              </div>
            </div>
          </div>

          <div className="card-actions">
            {/* LOC-20: Mark Complete button - ONLY shown for non-rest workouts */}
            {workout.status !== 'rest' && (
              <button
                onClick={onToggle}
                className={`btn-icon complete ${workout.status === 'completed' ? 'active' : ''} ${justCompleted ? 'checkmark-pop' : ''}`}
                aria-label={workout.status === 'completed' ? 'Mark as incomplete' : 'Mark as complete'}
              >
                <Check className="w-5 h-5" />
              </button>
            )}
            {/* Edit button - ALWAYS shown (LOC-20: allows editing rest days) */}
            <button
              onClick={onEdit}
              className="btn-icon"
              aria-label="Edit workout"
            >
              <Edit2 className="w-4 h-4" />
            </button>
          </div>
        </>
      ) : (
        <div className="mt-4 text-xs text-gray-400 italic">
          No workout scheduled
        </div>
      )}
    </div>
  );
}

