import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { WorkoutCard } from './WorkoutCard';
import { MonthView } from './MonthView';
import { ChevronLeft, ChevronRight, Calendar, LayoutGrid } from 'lucide-react';
import { mapWorkoutToDesign, getWorkoutStatus } from '../utils/workoutMapper';

const API_BASE_URL = '/api';

export function WeekAheadView() {
  const [viewMode, setViewMode] = useState('week');
  const [workouts, setWorkouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [weekOffset, setWeekOffset] = useState(0);
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1);
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  const [progress, setProgress] = useState({ completed: 0, total: 0 });

  // Fetch workouts for current week
  const fetchWeekWorkouts = async (offset = 0) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE_URL}/workouts/week/${offset}`);
      const dbWorkouts = response.data.workouts || [];
      
      // Map to design format
      const mappedWorkouts = dbWorkouts.map(mapWorkoutToDesign);
      
      // Create a map of day names to workouts
      const dayMap = {};
      mappedWorkouts.forEach(workout => {
        if (workout.day) {
          dayMap[workout.day] = workout;
        }
      });
      
      // Get week start date to determine which days are in this week
      const weekStart = response.data.week_start ? new Date(response.data.week_start) : null;
      const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      
      // Ensure we have workouts for all 7 days (Mon-Sun)
      const weekWorkouts = dayNames.map((day, index) => {
        if (dayMap[day]) {
          return dayMap[day];
        }
        // Create placeholder for missing days
        // If we have week_start, we can calculate the actual date
        let scheduledDate = null;
        if (weekStart) {
          const date = new Date(weekStart);
          date.setDate(date.getDate() + index);
          scheduledDate = date.toISOString().split('T')[0];
        }
        
        return {
          id: `placeholder-${day}`,
          day: day,
          type: '',
          distance: '',
          status: 'pending',
          scheduledDate: scheduledDate,
          _original: null
        };
      });
      
      setWorkouts(weekWorkouts);
      
      // Fetch progress
      const progressResponse = await axios.get(`${API_BASE_URL}/workouts/progress`, {
        params: { week_offset: offset }
      });
      setProgress({
        completed: progressResponse.data.completed_count || 0,
        total: progressResponse.data.total_count || 0
      });
    } catch (err) {
      console.error('Error fetching week workouts:', err);
      setError(err.response?.data?.error || 'Failed to load workouts');
      setWorkouts([]);
    } finally {
      setLoading(false);
    }
  };

  // Fetch workouts for current month
  const fetchMonthWorkouts = async (year, month) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE_URL}/workouts/month/${year}/${month}`);
      const dbWorkouts = response.data.workouts || [];
      
      // Map to design format
      const mappedWorkouts = dbWorkouts.map(mapWorkoutToDesign);
      setWorkouts(mappedWorkouts);
    } catch (err) {
      console.error('Error fetching month workouts:', err);
      setError(err.response?.data?.error || 'Failed to load workouts');
      setWorkouts([]);
    } finally {
      setLoading(false);
    }
  };

  // Load data when view mode or offset changes
  useEffect(() => {
    if (viewMode === 'week') {
      fetchWeekWorkouts(weekOffset);
    } else {
      fetchMonthWorkouts(currentYear, currentMonth);
    }
  }, [viewMode, weekOffset, currentMonth, currentYear]);

  // Toggle workout completion
  const toggleWorkoutStatus = async (workoutId) => {
    // Skip placeholder workouts
    if (workoutId.startsWith('placeholder-')) return;
    
    try {
      const response = await axios.put(`${API_BASE_URL}/workouts/${workoutId}/complete`);
      const updatedWorkout = mapWorkoutToDesign(response.data.workout);
      
      // Update workouts array
      setWorkouts(prevWorkouts => 
        prevWorkouts.map(w => w.id === workoutId ? updatedWorkout : w)
      );
      
      // Refresh progress
      if (viewMode === 'week') {
        const progressResponse = await axios.get(`${API_BASE_URL}/workouts/progress`, {
          params: { week_offset: weekOffset }
        });
        setProgress({
          completed: progressResponse.data.completed_count || 0,
          total: progressResponse.data.total_count || 0
        });
      }
    } catch (err) {
      console.error('Error toggling workout status:', err);
      setError(err.response?.data?.error || 'Failed to update workout');
    }
  };

  // Handle edit (placeholder for now)
  const handleEdit = (workoutId) => {
    // Skip placeholder workouts
    if (workoutId.startsWith('placeholder-')) return;
    
    // TODO: Implement edit modal/form in Phase 7
    console.log('Edit workout:', workoutId);
    alert('Edit functionality coming in Phase 7!');
  };

  // Navigation handlers
  const handlePrevious = () => {
    if (viewMode === 'week') {
      setWeekOffset(prev => prev - 1);
    } else {
      // Previous month
      if (currentMonth === 1) {
        setCurrentMonth(12);
        setCurrentYear(prev => prev - 1);
      } else {
        setCurrentMonth(prev => prev - 1);
      }
    }
  };

  const handleNext = () => {
    if (viewMode === 'week') {
      setWeekOffset(prev => prev + 1);
    } else {
      // Next month
      if (currentMonth === 12) {
        setCurrentMonth(1);
        setCurrentYear(prev => prev + 1);
      } else {
        setCurrentMonth(prev => prev + 1);
      }
    }
  };

  // Get week range for display
  const getWeekRange = () => {
    const today = new Date();
    const currentDay = today.getDay();
    const diff = today.getDate() - currentDay + (currentDay === 0 ? -6 : 1); // Adjust when day is Sunday
    const monday = new Date(today.setDate(diff));
    monday.setDate(monday.getDate() + (weekOffset * 7));
    const sunday = new Date(monday);
    sunday.setDate(sunday.getDate() + 6);
    
    return {
      start: monday.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      end: sunday.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    };
  };

  const weekRange = viewMode === 'week' ? getWeekRange() : null;
  const monthName = new Date(currentYear, currentMonth - 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

  if (loading && workouts.length === 0) {
    return (
      <div className="max-w-full mx-auto p-6">
        <div className="bg-white rounded-lg shadow-sm border border-[#8eb19d] p-6">
          <div className="text-center text-[#1e1b18]">Loading workouts...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-full mx-auto p-6">
      <div className="bg-white rounded-lg shadow-sm border border-[#8eb19d]">
        {/* Header */}
        <div className="p-6 border-b border-[#8eb19d]">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-semibold text-[#1e1b18]">
              {viewMode === 'week' 
                ? `Your Week Ahead${weekRange ? ` (${weekRange.start} - ${weekRange.end})` : ''}`
                : `Your Month Ahead (${monthName})`
              }
            </h1>
            <div className="flex items-center gap-2">
              <button 
                onClick={() => {
                  const newMode = viewMode === 'week' ? 'month' : 'week';
                  setViewMode(newMode);
                  if (newMode === 'week') {
                    // Reset to current week when switching to week view
                    setWeekOffset(0);
                  } else {
                    // Set to current month when switching to month view
                    const now = new Date();
                    setCurrentMonth(now.getMonth() + 1);
                    setCurrentYear(now.getFullYear());
                  }
                }}
                className="px-4 py-2 text-sm border border-[#8eb19d] text-[#1e1b18] rounded-lg hover:bg-[#eacdc2] flex items-center gap-2"
              >
                {viewMode === 'week' ? (
                  <>
                    <Calendar className="w-4 h-4" />
                    Month View
                  </>
                ) : (
                  <>
                    <LayoutGrid className="w-4 h-4" />
                    Week View
                  </>
                )}
              </button>
              <button 
                onClick={handlePrevious}
                className="p-2 border border-[#8eb19d] text-[#1e1b18] rounded-lg hover:bg-[#eacdc2]"
                aria-label={viewMode === 'week' ? 'Previous week' : 'Previous month'}
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button 
                onClick={handleNext}
                className="p-2 border border-[#8eb19d] text-[#1e1b18] rounded-lg hover:bg-[#eacdc2]"
                aria-label={viewMode === 'week' ? 'Next week' : 'Next month'}
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
          {error && (
            <div className="mb-2 text-sm text-red-600 bg-red-50 p-2 rounded">
              {error}
            </div>
          )}
          {viewMode === 'week' && (
            <div className="text-sm text-[#1e1b18]">
              Progress: <span className="font-medium text-[#072ac8]">{progress.completed}/{progress.total}</span> workouts completed
            </div>
          )}
        </div>

        {/* View Content */}
        {viewMode === 'week' ? (
          <div className="p-6 overflow-x-auto">
            {workouts.length === 0 ? (
              <div className="text-center text-[#1e1b18]/60 py-8">
                No workouts scheduled for this week. Create a workout plan to get started!
              </div>
            ) : (
              <div className="grid grid-cols-7 gap-4 min-w-max">
                {workouts.map((workout) => (
                  <WorkoutCard
                    key={workout.id}
                    workout={workout}
                    onToggle={() => toggleWorkoutStatus(workout.id)}
                    onEdit={() => handleEdit(workout.id)}
                  />
                ))}
              </div>
            )}
          </div>
        ) : (
          <MonthView 
            workouts={workouts}
            onToggle={toggleWorkoutStatus}
            onEdit={handleEdit}
            currentMonth={currentMonth}
            currentYear={currentYear}
          />
        )}
      </div>
    </div>
  );
}

