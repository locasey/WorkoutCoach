import React from 'react';
import { Check, Minus, Edit2, MessageSquare } from 'lucide-react';

export function MonthView({ workouts, onToggle, onEdit, onDayClick, currentMonth, currentYear }) {
  // Check if a date is today
  const isToday = (fullDate) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const compareDate = new Date(fullDate);
    compareDate.setHours(0, 0, 0, 0);
    return today.getTime() === compareDate.getTime();
  };
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

    // Create a map of scheduled dates to workouts for efficient lookup
    const workoutMap = new Map();
    workouts.forEach(w => {
      if (w._original?.scheduled_date) {
        // scheduled_date comes as ISO string "YYYY-MM-DD"
        workoutMap.set(w._original.scheduled_date, w);
      }
    });

    // Add previous month days
    const prevMonthLastDay = new Date(currentYear, currentMonth - 1, 0).getDate();
    const prevMonth = currentMonth === 1 ? 12 : currentMonth - 1;
    const prevYear = currentMonth === 1 ? currentYear - 1 : currentYear;
    for (let i = startDay - 1; i >= 0; i--) {
      const prevDate = prevMonthLastDay - i;
      const dateStr = `${prevYear}-${String(prevMonth).padStart(2, '0')}-${String(prevDate).padStart(2, '0')}`;
      calendar.push({
        date: prevDate,
        fullDate: new Date(prevYear, prevMonth - 1, prevDate),
        isCurrentMonth: false,
        workout: workoutMap.get(dateStr) || null
      });
    }

    // Add current month days
    for (let date = 1; date <= daysInMonth; date++) {
      const dateStr = `${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(date).padStart(2, '0')}`;

      calendar.push({
        date,
        fullDate: new Date(currentYear, currentMonth - 1, date),
        isCurrentMonth: true,
        workout: workoutMap.get(dateStr) || null
      });
    }

    // Add next month days to complete the grid (42 cells = 6 weeks)
    const remainingDays = 42 - calendar.length;
    const nextMonth = currentMonth === 12 ? 1 : currentMonth + 1;
    const nextYear = currentMonth === 12 ? currentYear + 1 : currentYear;
    for (let i = 1; i <= remainingDays; i++) {
      const dateStr = `${nextYear}-${String(nextMonth).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
      calendar.push({
        date: i,
        fullDate: new Date(nextYear, nextMonth - 1, i),
        isCurrentMonth: false,
        workout: workoutMap.get(dateStr) || null
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

  const hasWorkouts = workouts.length > 0 && workouts.some(w => w._original?.scheduled_date);

  return (
    <div className="p-6">
      {!hasWorkouts ? (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <MessageSquare className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-semibold text-carbon-black mb-2">
              No workouts scheduled
            </h3>
            <p className="text-gray-600 mb-6">
              Get started by creating a personalized workout plan through the Chat interface.
            </p>
            <button
              onClick={() => {
                const chatTab = document.getElementById('tab-chat');
                if (chatTab) chatTab.click();
              }}
              className="inline-flex items-center gap-2 px-6 py-3 bg-persian-blue text-white rounded-lg hover:bg-persian-blue-hover transition-colors font-medium"
            >
              <MessageSquare className="w-5 h-5" />
              Create Workout Plan
            </button>
          </div>
        </div>
      ) : (
        <>
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
            {calendar.map((day, index) => {
              const isTodayCell = isToday(day.fullDate);
              return (
                <div
                  key={index}
                  onClick={() => onDayClick && onDayClick(day.fullDate)}
                  className={`border rounded-lg p-3 min-h-[120px] cursor-pointer transition-all ${
                    day.isCurrentMonth
                      ? 'bg-white border-[#8eb19d]'
                      : 'bg-[#eacdc2]/30 border-[#eacdc2]'
                  } ${day.workout ? 'hover:shadow-md' : 'hover:bg-[#eacdc2]/20'} ${
                    isTodayCell ? 'ring-2 ring-persian-blue ring-offset-1' : ''
                  }`}
                >
                  {/* Date */}
                  <div className={`text-sm font-medium mb-2 flex items-center justify-between ${
                    day.isCurrentMonth ? 'text-[#1e1b18]' : 'text-[#1e1b18]/40'
                  }`}>
                    <span>{day.date}</span>
                    {isTodayCell && (
                      <div className="w-2 h-2 bg-persian-blue rounded-full"></div>
                    )}
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
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggle(day.workout.id);
                    }}
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
                    onClick={(e) => {
                      e.stopPropagation();
                      onEdit(day.workout.id);
                    }}
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
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

