import React, { useState } from 'react';
import { Check, Minus, Edit2, Clock, Gauge, Heart, StickyNote, ChevronDown, ChevronUp, Calendar } from 'lucide-react';

export function WorkoutCard({ workout, onToggle, onEdit, isToday = false }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStatusIcon = () => {
    if (workout.status === 'completed') {
      return <Check className="w-4 h-4 text-[#8eb19d]" />;
    }
    if (workout.status === 'rest') {
      return <Minus className="w-4 h-4 text-[#a44200]" />;
    }
    return null;
  };

  const getCardStyles = () => {
    if (workout.status === 'completed') {
      return 'border-[#8eb19d] bg-[#8eb19d]/10';
    }
    if (workout.status === 'rest') {
      return 'border-[#a44200] bg-[#a44200]/10';
    }
    return 'border-[#072ac8] bg-white';
  };

  const getIntensityColor = (intensity) => {
    switch (intensity) {
      case 'low':
        return 'bg-[#8eb19d]';
      case 'moderate':
        return 'bg-[#072ac8]';
      case 'high':
        return 'bg-[#a44200]';
      default:
        return 'bg-gray-300';
    }
  };

  const isEmpty = !workout.type || workout.id?.startsWith('placeholder-');

  return (
    <div className={`border-2 rounded-lg p-4 transition-all min-w-[140px] ${getCardStyles()} ${isToday ? 'ring-2 ring-persian-blue ring-offset-2' : ''}`}>
      {/* Day Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm font-medium text-[#1e1b18]/60">{workout.day}</div>
        {isToday && (
          <div className="flex items-center gap-1 text-xs font-semibold text-persian-blue">
            <Calendar className="w-3 h-3" />
            Today
          </div>
        )}
      </div>
      
      {/* Workout Content - Clickable (only if not empty) */}
      {!isEmpty ? (
        <div 
          className="mb-4 cursor-pointer"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="font-medium text-[#1e1b18] mb-1 flex items-center justify-between">
            <span>{workout.type}</span>
            {workout.status !== 'rest' && (
              isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
            )}
          </div>
          {workout.distance && (
            <div className="text-sm text-[#1e1b18]/70">{workout.distance}</div>
          )}
        </div>
      ) : (
        <div className="mb-4 text-sm text-[#1e1b18]/40 italic">
          No workout scheduled
        </div>
      )}

      {/* Expanded Details */}
      {isExpanded && workout.status !== 'rest' && (
        <div className="mb-4 space-y-2 pb-3 border-b border-[#1e1b18]/10">
          {workout.duration && (
            <div className="flex items-center gap-2 text-sm text-[#1e1b18]/70">
              <Clock className="w-4 h-4 text-[#072ac8]" />
              <span>{workout.duration}</span>
            </div>
          )}
          {workout.pace && (
            <div className="flex items-center gap-2 text-sm text-[#1e1b18]/70">
              <Gauge className="w-4 h-4 text-[#072ac8]" />
              <span>{workout.pace}</span>
            </div>
          )}
          {workout.heartRateZone && (
            <div className="flex items-center gap-2 text-sm text-[#1e1b18]/70">
              <Heart className="w-4 h-4 text-[#a44200]" />
              <span>{workout.heartRateZone}</span>
            </div>
          )}
          {workout.intensity && (
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs text-[#1e1b18]/60 mb-1">
                <span>Intensity</span>
                <span className="capitalize">{workout.intensity}</span>
              </div>
              <div className="h-2 bg-[#eacdc2] rounded-full overflow-hidden">
                <div 
                  className={`h-full transition-all ${getIntensityColor(workout.intensity)}`}
                  style={{ 
                    width: workout.intensity === 'low' ? '33%' : 
                           workout.intensity === 'moderate' ? '66%' : '100%' 
                  }}
                />
              </div>
            </div>
          )}
          {workout.notes && (
            <div className="mt-2 p-2 bg-[#eacdc2]/40 rounded text-xs text-[#1e1b18]/70 flex items-start gap-2">
              <StickyNote className="w-3 h-3 mt-0.5 flex-shrink-0 text-[#072ac8]" />
              <span>{workout.notes}</span>
            </div>
          )}
        </div>
      )}

      {/* Status Checkbox - Only show if not empty */}
      {!isEmpty && (
        <div className="flex items-center justify-between">
          <button
            onClick={onToggle}
            disabled={workout.status === 'rest'}
            className={`w-6 h-6 border-2 rounded flex items-center justify-center transition-colors ${
              workout.status === 'completed'
                ? 'border-[#8eb19d] bg-[#8eb19d]'
                : workout.status === 'rest'
                ? 'border-[#a44200] bg-[#a44200] cursor-not-allowed'
                : 'border-[#072ac8] hover:border-[#072ac8]/70'
            }`}
          >
            {getStatusIcon()}
          </button>

          <button
            onClick={onEdit}
            className="p-1.5 text-[#1e1b18]/60 hover:text-[#072ac8] hover:bg-[#eacdc2] rounded transition-colors"
            aria-label="Edit workout"
          >
            <Edit2 className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}

