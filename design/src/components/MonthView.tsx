import React from 'react';
import { Check, Minus, Edit2 } from 'lucide-react';

type WorkoutStatus = 'completed' | 'rest' | 'pending';

interface Workout {
  id: string;
  day: string;
  type: string;
  distance: string;
  status: WorkoutStatus;
  duration?: string;
  pace?: string;
  intensity?: 'low' | 'moderate' | 'high';
  heartRateZone?: string;
  notes?: string;
}

interface MonthViewProps {
  workouts: Workout[];
  onToggle: (id: string) => void;
  onEdit: (id: string) => void;
}

interface DayData {
  date: number;
  isCurrentMonth: boolean;
  workout?: Workout;
}

export function MonthView({ workouts, onToggle, onEdit }: MonthViewProps) {
  // Generate calendar data for January 2026
  const generateCalendar = (): DayData[] => {
    const calendar: DayData[] = [];
    
    // January 2026 starts on Thursday (4th day of week)
    // Add previous month days (December 2025)
    const startDay = 4; // Thursday
    for (let i = startDay - 1; i >= 0; i--) {
      calendar.push({
        date: 29 + i,
        isCurrentMonth: false,
      });
    }
    
    // Add current month days (January has 31 days)
    const daysInMonth = 31;
    const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    
    for (let date = 1; date <= daysInMonth; date++) {
      const dayIndex = (date + startDay - 1) % 7;
      const dayName = dayNames[dayIndex];
      
      // Map workouts to specific dates (week 2 of the month: Jan 6-12)
      let workout: Workout | undefined;
      if (date >= 6 && date <= 12) {
        const workoutIndex = date - 6;
        workout = workouts[workoutIndex];
      }
      
      calendar.push({
        date,
        isCurrentMonth: true,
        workout,
      });
    }
    
    // Add next month days to complete the grid
    const remainingDays = 35 - calendar.length;
    for (let i = 1; i <= remainingDays; i++) {
      calendar.push({
        date: i,
        isCurrentMonth: false,
      });
    }
    
    return calendar;
  };

  const calendar = generateCalendar();
  const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  const getStatusIcon = (status: WorkoutStatus) => {
    if (status === 'completed') {
      return <Check className="w-3 h-3 text-[#8eb19d]" />;
    }
    if (status === 'rest') {
      return <Minus className="w-3 h-3 text-[#a44200]" />;
    }
    return null;
  };

  const getWorkoutDotColor = (status: WorkoutStatus) => {
    if (status === 'completed') return 'bg-[#8eb19d]';
    if (status === 'rest') return 'bg-[#a44200]';
    return 'bg-[#072ac8]';
  };

  return (
    <div className="p-6">
      {/* Week day headers */}
      <div className="grid grid-cols-7 gap-2 mb-2">
        {weekDays.map((day) => (
          <div key={day} className="text-center text-sm font-medium text-[#1e1b18]/60 py-2">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-2">
        {calendar.map((day, index) => (
          <div
            key={index}
            className={`border rounded-lg p-3 min-h-[120px] ${
              day.isCurrentMonth
                ? 'bg-white border-[#8eb19d]'
                : 'bg-[#eacdc2]/30 border-[#eacdc2]'
            } ${day.workout ? 'hover:shadow-md transition-shadow' : ''}`}
          >
            {/* Date */}
            <div className={`text-sm font-medium mb-2 ${
              day.isCurrentMonth ? 'text-[#1e1b18]' : 'text-[#1e1b18]/40'
            }`}>
              {day.date}
            </div>

            {/* Workout info */}
            {day.workout && (
              <div className="space-y-2">
                <div className={`text-xs font-medium ${
                  day.workout.status === 'completed' ? 'text-[#8eb19d]' :
                  day.workout.status === 'rest' ? 'text-[#a44200]' :
                  'text-[#072ac8]'
                }`}>
                  {day.workout.type}
                </div>
                {day.workout.distance && (
                  <div className="text-xs text-[#1e1b18]/70">{day.workout.distance}</div>
                )}
                
                {/* Actions */}
                <div className="flex items-center gap-2 pt-1">
                  <button
                    onClick={() => onToggle(day.workout!.id)}
                    disabled={day.workout.status === 'rest'}
                    className={`w-5 h-5 border-2 rounded flex items-center justify-center transition-colors ${
                      day.workout.status === 'completed'
                        ? 'border-[#8eb19d] bg-[#8eb19d]'
                        : day.workout.status === 'rest'
                        ? 'border-[#a44200] bg-[#a44200] cursor-not-allowed'
                        : 'border-[#072ac8] hover:border-[#072ac8]/70'
                    }`}
                  >
                    {getStatusIcon(day.workout.status)}
                  </button>
                  
                  <button
                    onClick={() => onEdit(day.workout!.id)}
                    className="p-1 text-[#1e1b18]/60 hover:text-[#072ac8] hover:bg-[#eacdc2] rounded transition-colors"
                    aria-label="Edit workout"
                  >
                    <Edit2 className="w-3 h-3" />
                  </button>
                  
                  <div className={`ml-auto w-2 h-2 rounded-full ${getWorkoutDotColor(day.workout.status)}`} />
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}