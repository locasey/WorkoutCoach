import React from 'react';
import { Check, Minus, Edit2 } from 'lucide-react';

export function MonthView({ workouts, onToggle, onEdit, currentMonth, currentYear }) {
  // Generate calendar data for the current month
  const generateCalendar = () => {
    const calendar = [];
    
    // Get first day of month and number of days
    const firstDay = new Date(currentYear, currentMonth - 1, 1);
    const lastDay = new Date(currentYear, currentMonth, 0);
    const daysInMonth = lastDay.getDate();
    
    // Get day of week for first day (0 = Sunday, we want Monday = 0)
    let startDay = firstDay.getDay() - 1;
    if (startDay < 0) startDay = 6; // Sunday becomes 6
    
    // Add previous month days
    const prevMonthLastDay = new Date(currentYear, currentMonth - 1, 0).getDate();
    for (let i = startDay - 1; i >= 0; i--) {
      calendar.push({
        date: prevMonthLastDay - i,
        isCurrentMonth: false,
        workout: null
      });
    }
    
    // Add current month days
    for (let date = 1; date <= daysInMonth; date++) {
      const dateStr = `${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(date).padStart(2, '0')}`;
      
      // Find workout for this date
      const workout = workouts.find(w => {
        if (!w._original?.scheduled_date) return false;
        const workoutDate = new Date(w._original.scheduled_date);
        return workoutDate.getFullYear() === currentYear &&
               workoutDate.getMonth() + 1 === currentMonth &&
               workoutDate.getDate() === date;
      });
      
      calendar.push({
        date,
        isCurrentMonth: true,
        workout: workout || null
      });
    }
    
    // Add next month days to complete the grid (42 cells = 6 weeks)
    const remainingDays = 42 - calendar.length;
    for (let i = 1; i <= remainingDays; i++) {
      calendar.push({
        date: i,
        isCurrentMonth: false,
        workout: null
      });
    }
    
    return calendar;
  };

  const calendar = generateCalendar();
  const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  const getStatusIcon = (status) => {
    if (status === 'completed') {
      return <Check className="w-3 h-3 text-[#8eb19d]" />;
    }
    if (status === 'rest') {
      return <Minus className="w-3 h-3 text-[#a44200]" />;
    }
    return null;
  };

  const getWorkoutDotColor = (status) => {
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
                    onClick={() => onToggle(day.workout.id)}
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
                    onClick={() => onEdit(day.workout.id)}
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

