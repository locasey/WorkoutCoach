import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useSwipeable } from 'react-swipeable';
import { WorkoutCard } from './WorkoutCard';
import { MonthView } from './MonthView';
import { WorkoutEditModal } from './WorkoutEditModal';
import { ChevronLeft, ChevronRight, Calendar, LayoutGrid, MessageSquare, CheckCircle, Clock, MapPin, Edit3, Plus } from 'lucide-react';
import { mapWorkoutToDesign, getWorkoutStatus } from '../utils/workoutMapper';
import { SkeletonWeek, SkeletonMonth } from './SkeletonLoader';
import { useToast } from './Toast';
import { ErrorAlert } from './ErrorAlert';
import './WeekAheadView.css';

const API_BASE_URL = '/api';

export function WeekAheadView({ initialView = 'week' }) {
  const [viewMode, setViewMode] = useState(initialView);
  const [workouts, setWorkouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [weekOffset, setWeekOffset] = useState(0);
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1);
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  const [progress, setProgress] = useState({ completed: 0, total: 0 });
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);
  const toast = useToast();

  // Edit modal state
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedWorkout, setSelectedWorkout] = useState(null);

  // LOC-22: Grouped workouts by day (supports multiple workouts per day)
  const [groupedWorkouts, setGroupedWorkouts] = useState({});
  // Active plan ID for adding workouts
  const [activePlanId, setActivePlanId] = useState(null);

  // Fetch workouts for current week
  const fetchWeekWorkouts = async (offset = 0) => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.get(`${API_BASE_URL}/workouts/week/${offset}`);
      const dbWorkouts = response.data.workouts || [];

      // Map to design format
      const mappedWorkouts = dbWorkouts.map(mapWorkoutToDesign);

      // LOC-22: Group workouts by scheduled date (supports multiple workouts per day)
      // Create a map of scheduled_date to array of workouts
      const dateMap = {};
      mappedWorkouts.forEach(workout => {
        const key = workout.scheduledDate || workout.day;
        if (!dateMap[key]) {
          dateMap[key] = [];
        }
        dateMap[key].push(workout);
        // Sort by slot (null first, then 1=AM, then 2=PM)
        dateMap[key].sort((a, b) => (a.slot || 0) - (b.slot || 0));
      });

      // Get week start date to determine which days are in this week
      const weekStart = response.data.week_start ? new Date(response.data.week_start) : null;
      const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

      // Build week structure: each day can have 1-2 workouts
      // For backward compatibility, the workouts array contains all workouts
      // but we also store groupedWorkouts for multi-workout display
      const allWorkouts = [];
      const groupedByDay = {};

      dayNames.forEach((day, index) => {
        // Calculate the scheduled date for this day
        let scheduledDate = null;
        if (weekStart) {
          const date = new Date(weekStart);
          date.setDate(date.getDate() + index);
          scheduledDate = date.toISOString().split('T')[0];
        }

        // Check if we have workouts for this date
        const dayWorkouts = dateMap[scheduledDate] || dateMap[day] || [];

        if (dayWorkouts.length > 0) {
          // Add all workouts for this day
          dayWorkouts.forEach(w => allWorkouts.push(w));
          groupedByDay[day] = dayWorkouts;
        } else {
          // Create placeholder for missing days
          const placeholder = {
            id: `placeholder-${day}`,
            day: day,
            type: '',
            distance: '',
            status: 'pending',
            scheduledDate: scheduledDate,
            slot: null,
            _original: null
          };
          allWorkouts.push(placeholder);
          groupedByDay[day] = [placeholder];
        }
      });

      // Store both flat list (for backward compat) and grouped structure
      setWorkouts(allWorkouts);
      setGroupedWorkouts(groupedByDay);

      // Get active plan ID from first workout (for adding new workouts)
      if (allWorkouts.length > 0 && allWorkouts[0]._original?.workout_plan_id) {
        setActivePlanId(allWorkouts[0]._original.workout_plan_id);
      }

      // Set initial selected day index to today if we're in the current week
      if (offset === 0) {
        // Find today in the day names array
        const today = new Date();
        const todayDayName = dayNames[today.getDay() === 0 ? 6 : today.getDay() - 1];
        const todayIndex = dayNames.indexOf(todayDayName);
        if (todayIndex !== -1) {
          setSelectedDayIndex(todayIndex);
        }
      }

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

  // Handle window resize for mobile detection
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Don't navigate if modal is open or user is typing in an input
      if (editModalOpen || e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return;
      }

      switch (e.key) {
        case 'ArrowLeft':
          handlePrevious();
          break;
        case 'ArrowRight':
          handleNext();
          break;
        case 't':
        case 'T':
          // Go to today
          if (viewMode === 'week') {
            setWeekOffset(0);
          } else {
            const now = new Date();
            setCurrentMonth(now.getMonth() + 1);
            setCurrentYear(now.getFullYear());
          }
          break;
        default:
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [viewMode, editModalOpen]);

  // Toggle workout completion
  const toggleWorkoutStatus = async (workoutId) => {
    // Skip placeholder workouts
    if (workoutId.startsWith('placeholder-')) return;

    // Store the previous workout state for undo
    const previousWorkout = workouts.find(w => w.id === workoutId);
    if (!previousWorkout) return;

    try {
      const response = await axios.put(`${API_BASE_URL}/workouts/${workoutId}/complete`);
      const updatedWorkout = mapWorkoutToDesign(response.data.workout);

      // Update workouts array
      setWorkouts(prevWorkouts =>
        prevWorkouts.map(w => w.id === workoutId ? updatedWorkout : w)
      );

      // Show feedback with undo option
      const isCompleted = updatedWorkout.status === 'completed';
      
      if (isCompleted) {
        toast.success(
          'Workout marked as complete!',
          5000,
          {
            label: 'Undo',
            onClick: () => {
              // Call toggle again to undo
              toggleWorkoutStatus(workoutId);
            }
          }
        );
      } else {
        toast.success('Workout marked as incomplete');
      }

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
      const errorMsg = err.response?.data?.error || 'Failed to update workout';
      setError(errorMsg);
      toast.error(errorMsg);
    }
  };

  // Handle edit - open modal
  const handleEdit = (workoutId) => {
    // Skip placeholder workouts
    if (workoutId.startsWith('placeholder-')) return;

    const workout = workouts.find(w => w.id === workoutId);
    if (workout) {
      setSelectedWorkout(workout);
      setEditModalOpen(true);
    }
  };

  // Handle save from edit modal
  const handleSaveWorkout = (updatedDbWorkout) => {
    const updatedWorkout = mapWorkoutToDesign(updatedDbWorkout);

    // Update workouts array
    setWorkouts(prevWorkouts =>
      prevWorkouts.map(w => w.id === updatedWorkout.id ? updatedWorkout : w)
    );

    // Also update grouped workouts
    setGroupedWorkouts(prev => {
      const newGrouped = { ...prev };
      Object.keys(newGrouped).forEach(day => {
        newGrouped[day] = newGrouped[day].map(w =>
          w.id === updatedWorkout.id ? updatedWorkout : w
        );
      });
      return newGrouped;
    });
  };

  // LOC-22: Handle adding a new workout to a day
  const handleAddWorkout = async (scheduledDate) => {
    if (!activePlanId || !scheduledDate) {
      toast.error('Cannot add workout: no active plan');
      return;
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/workouts/day`, {
        workout_plan_id: activePlanId,
        scheduled_date: scheduledDate,
        type: 'easy_run',  // Default type
        duration_minutes: 30,
        notes: 'New workout added'
      });

      const newWorkout = mapWorkoutToDesign(response.data.workout);

      // Refresh the week to get updated data
      fetchWeekWorkouts(weekOffset);

      toast.success('Workout added! Edit it to customize.');
    } catch (err) {
      console.error('Error adding workout:', err);
      const errorMsg = err.response?.data?.error || 'Failed to add workout';
      toast.error(errorMsg);
    }
  };

  // Handle day click from month view - navigate to that week in week view
  const handleDayClick = (date) => {
    if (!date) return;

    // Calculate the week offset from today
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Get the Monday of today's week
    const todayDayOfWeek = today.getDay();
    const todayMonday = new Date(today);
    todayMonday.setDate(today.getDate() - (todayDayOfWeek === 0 ? 6 : todayDayOfWeek - 1));

    // Get the Monday of the clicked date's week
    const clickedDate = new Date(date);
    clickedDate.setHours(0, 0, 0, 0);
    const clickedDayOfWeek = clickedDate.getDay();
    const clickedMonday = new Date(clickedDate);
    clickedMonday.setDate(clickedDate.getDate() - (clickedDayOfWeek === 0 ? 6 : clickedDayOfWeek - 1));

    // Calculate week difference
    const diffTime = clickedMonday.getTime() - todayMonday.getTime();
    const diffWeeks = Math.round(diffTime / (7 * 24 * 60 * 60 * 1000));

    // Switch to week view with the calculated offset
    setWeekOffset(diffWeeks);
    setViewMode('week');
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

  // Swipe handlers for mobile week navigation
  const swipeHandlers = useSwipeable({
    onSwipedLeft: () => handleNext(),
    onSwipedRight: () => handlePrevious(),
    preventScrollOnSwipe: true,
    trackMouse: false
  });

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

  // Check if today is in the current week
  const isTodayInWeek = (scheduledDate) => {
    if (!scheduledDate) return false;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const workoutDate = new Date(scheduledDate);
    workoutDate.setHours(0, 0, 0, 0);
    return today.getTime() === workoutDate.getTime();
  };

  // LOC-22: Get active workout(s) from grouped structure based on selected day index
  const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const selectedDayName = dayNames[selectedDayIndex];
  const selectedDayWorkouts = groupedWorkouts[selectedDayName] || [];
  const activeWorkout = selectedDayWorkouts[0] || null; // Primary workout for hero display
  const isActiveToday = activeWorkout && isTodayInWeek(activeWorkout.scheduledDate);

  const weekRange = viewMode === 'week' ? getWeekRange() : null;
  const monthName = new Date(currentYear, currentMonth - 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

  return (
    <div className="max-w-full mx-auto p-4 sm:p-6">
      <div className="bg-white rounded-lg shadow-sm">
        {/* Header - Hidden on mobile, shown on desktop */}
        <div className="hidden md:block p-6">
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
                    setWeekOffset(0);
                  } else {
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
            <ErrorAlert
              message={error}
              onRetry={() => {
                setError(null);
                if (viewMode === 'week') {
                  fetchWeekWorkouts(weekOffset);
                } else {
                  fetchMonthWorkouts(currentYear, currentMonth);
                }
              }}
              onDismiss={() => setError(null)}
              className="mb-4"
            />
          )}
          {viewMode === 'week' && (
            <div className="text-sm text-[#1e1b18]">
              Progress: <span className="font-medium text-[#072ac8]">{progress.completed}/{progress.total}</span> workouts completed
            </div>
          )}
        </div>

        {/* Mobile View Navigation & Header */}
        <div className="md:hidden mb-6">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-bold text-carbon-black">
              {weekRange ? `${weekRange.start} - ${weekRange.end}` : ''}
            </h2>
            <div className="flex gap-1">
              <button onClick={handlePrevious} className="p-2 text-carbon-black"><ChevronLeft className="w-5 h-5" /></button>
              <button onClick={handleNext} className="p-2 text-carbon-black"><ChevronRight className="w-5 h-5" /></button>
            </div>
          </div>
          
          {/* Day Picker - LOC-22: Uses grouped workouts to show primary workout per day */}
          <div className="day-picker">
            {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, index) => {
              const dayWorkouts = groupedWorkouts[day] || [];
              const primaryWorkout = dayWorkouts[0]; // First/only workout for display
              const isToday = primaryWorkout && isTodayInWeek(primaryWorkout.scheduledDate);
              const isActive = selectedDayIndex === index;
              const hasMultiple = dayWorkouts.length > 1;

              // Display workout metric: duration > distance > Rest > --
              const getDisplayValue = () => {
                if (!primaryWorkout || !primaryWorkout.type) return '--';
                if (primaryWorkout.status === 'rest') return 'Rest';
                if (primaryWorkout.duration) return primaryWorkout.duration.replace(' ', '');
                if (primaryWorkout.distance) return primaryWorkout.distance;
                return '--';
              };

              // Get combined status for indicator (completed if all complete, rest if all rest)
              const getStatus = () => {
                if (!primaryWorkout || !primaryWorkout.type) return 'pending';
                if (dayWorkouts.every(w => w.status === 'completed')) return 'completed';
                if (dayWorkouts.every(w => w.status === 'rest')) return 'rest';
                if (dayWorkouts.some(w => w.status === 'completed')) return 'partial';
                return primaryWorkout.status;
              };

              return (
                <div
                  key={day}
                  className={`day-item ${isActive ? 'active' : ''} ${isToday ? 'today' : ''}`}
                  onClick={() => setSelectedDayIndex(index)}
                >
                  <span className="day-name">{day}</span>
                  <span className="day-number">
                    {getDisplayValue()}
                    {hasMultiple && <span className="text-xs ml-0.5">+1</span>}
                  </span>
                  <div className={`day-status-indicator status-${getStatus()}`} />
                </div>
              );
            })}
          </div>
        </div>

        {/* View Content */}
        {viewMode === 'week' ? (
          <div className="md:p-6" {...swipeHandlers}>
            {loading && workouts.length === 0 ? (
              <SkeletonWeek />
            ) : workouts.length === 0 || workouts.every(w => !w.type) ? (
              <div className="text-center py-12">
                <div className="max-w-md mx-auto">
                  <MessageSquare className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                  <h3 className="text-lg font-semibold text-carbon-black mb-2">
                    No workouts scheduled
                  </h3>
                  <p className="text-gray-600 mb-6 px-4">
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
                {/* Mobile: Today Hero Section - LOC-20 + LOC-22 */}
                <div className="md:hidden">
                  {activeWorkout && (
                    <div className="today-hero">
                      <div className="hero-header">
                        <div className="hero-label">
                          {isActiveToday ? 'Today\'s Training' : `${activeWorkout.day}'s Training`}
                        </div>
                        {activeWorkout.status === 'completed' && (
                          <div className="text-success-green flex items-center gap-1 font-bold text-xs">
                            <CheckCircle className="w-4 h-4" />
                            DONE
                          </div>
                        )}
                      </div>

                      <h3 className="hero-title">
                        {activeWorkout.status === 'rest' ? 'Rest Day' : (activeWorkout.type || 'No Workout')}
                      </h3>

                      {/* LOC-22: Show slot indicator if this day has multiple workouts */}
                      {activeWorkout.slot && (
                        <div className="text-xs text-gray-500 mb-2">
                          {activeWorkout.slot === 1 ? 'AM Session' : 'PM Session'}
                        </div>
                      )}

                      {/* Show metrics only for non-rest workouts */}
                      {activeWorkout.status !== 'rest' && activeWorkout.type && (
                        <>
                          <div className="hero-metrics">
                            <div className="hero-metric">
                              <span className="metric-value">{activeWorkout.duration || '--'}</span>
                              <span className="metric-label">Duration</span>
                            </div>
                            <div className="hero-metric">
                              <span className="metric-value">{activeWorkout.distance || '--'}</span>
                              <span className="metric-label">Distance</span>
                            </div>
                          </div>

                          {activeWorkout.notes && (
                            <p className="hero-description line-clamp-3">
                              {activeWorkout.notes}
                            </p>
                          )}
                        </>
                      )}

                      {/* LOC-20: Rest day message */}
                      {activeWorkout.status === 'rest' && (
                        <p className="hero-description mt-4">
                          Enjoy your rest day! Recovery is just as important as the work.
                        </p>
                      )}

                      {/* LOC-20: Action buttons - Edit always shown, Mark Complete only for non-rest */}
                      {activeWorkout.type && (
                        <div className="hero-actions">
                          {/* Mark Complete - ONLY for non-rest workouts */}
                          {activeWorkout.status !== 'rest' && (
                            <button
                              onClick={() => toggleWorkoutStatus(activeWorkout.id)}
                              className={`btn-hero ${activeWorkout.status === 'completed' ? 'btn-hero-secondary' : 'btn-hero-primary'}`}
                            >
                              <CheckCircle className="w-5 h-5" />
                              {activeWorkout.status === 'completed' ? 'Unmark Complete' : 'Mark Complete'}
                            </button>
                          )}

                          {/* Edit - ALWAYS shown (LOC-20 fix for rest days) */}
                          <button
                            onClick={() => handleEdit(activeWorkout.id)}
                            className={`btn-hero ${activeWorkout.status === 'rest' ? 'btn-hero-primary' : 'btn-hero-secondary'}`}
                          >
                            <Edit3 className="w-5 h-5" />
                            Edit
                          </button>

                          {/* LOC-22: Add Workout button when day has < 2 workouts */}
                          {activePlanId && activeWorkout.scheduledDate && (() => {
                            const dayWorkouts = groupedWorkouts[activeWorkout.day] || [];
                            return dayWorkouts.length < 2 && (
                              <button
                                onClick={() => handleAddWorkout(activeWorkout.scheduledDate)}
                                className="btn-hero btn-hero-secondary"
                              >
                                <Plus className="w-5 h-5" />
                                Add Workout
                              </button>
                            );
                          })()}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Desktop: Grid Layout - LOC-22: Support multiple workouts per day */}
                <div className="hidden md:grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
                  {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => {
                    const dayWorkouts = groupedWorkouts[day] || [];
                    const firstWorkout = dayWorkouts[0];
                    const hasMultiple = dayWorkouts.length > 1;

                    return (
                      <div key={day} className="workout-day-column flex flex-col gap-2">
                        {dayWorkouts.map((workout, idx) => (
                          <WorkoutCard
                            key={workout.id}
                            workout={workout}
                            isToday={isTodayInWeek(workout.scheduledDate)}
                            onToggle={() => toggleWorkoutStatus(workout.id)}
                            onEdit={() => handleEdit(workout.id)}
                            isAM={hasMultiple && idx === 0}
                            isPM={hasMultiple && idx === 1}
                          />
                        ))}
                        {/* LOC-22: Add Workout button when day has < 2 workouts */}
                        {activePlanId && firstWorkout?.scheduledDate && dayWorkouts.length < 2 && (
                          <button
                            onClick={() => handleAddWorkout(firstWorkout.scheduledDate)}
                            className="w-full p-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-persian-blue hover:text-persian-blue transition-colors flex items-center justify-center gap-1 text-sm"
                          >
                            <Plus className="w-4 h-4" />
                            Add
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </>
            )}
          </div>
        ) : (
          loading && workouts.length === 0 ? (
            <SkeletonMonth />
          ) : (
            <MonthView
              workouts={workouts}
              onToggle={toggleWorkoutStatus}
              onEdit={handleEdit}
              onDayClick={handleDayClick}
              currentMonth={currentMonth}
              currentYear={currentYear}
            />
          )
        )}
      </div>

      <WorkoutEditModal
        isOpen={editModalOpen}
        onClose={() => {
          setEditModalOpen(false);
          setSelectedWorkout(null);
        }}
        workout={selectedWorkout}
        onSave={handleSaveWorkout}
      />
    </div>
  );
}

