import React, { useState, useEffect } from 'react';
import { Check, Minus, Edit2, Clock, Gauge, Heart, StickyNote, ChevronDown, ChevronUp, Calendar, Zap } from 'lucide-react';
import confetti from 'canvas-confetti';
import './WorkoutCard.css';

export function WorkoutCard({ workout, onToggle, onEdit, isToday = false }) {
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
        <span className="card-day">{workout.day}</span>
        {isToday && (
          <div className="flex items-center gap-1 text-[10px] font-bold text-persian-blue uppercase">
            <Calendar className="w-3 h-3" />
            Today
          </div>
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
                <span className="actual-value">--</span>
              </div>
            </div>
          </div>

          <div className="card-actions">
            <button
              onClick={onToggle}
              disabled={workout.status === 'rest'}
              className={`btn-icon complete ${workout.status === 'completed' ? 'active' : ''} ${justCompleted ? 'checkmark-pop' : ''}`}
              aria-label={workout.status === 'completed' ? 'Mark as incomplete' : 'Mark as complete'}
            >
              <Check className="w-5 h-5" />
            </button>
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

