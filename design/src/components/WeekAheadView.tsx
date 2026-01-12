import React, { useState } from 'react';
import { WorkoutCard } from './WorkoutCard';
import { MonthView } from './MonthView';
import { ChevronLeft, ChevronRight, Calendar, LayoutGrid } from 'lucide-react';

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

export function WeekAheadView() {
  const [viewMode, setViewMode] = useState<'week' | 'month'>('week');
  const [workouts, setWorkouts] = useState<Workout[]>([
    { 
      id: '1', 
      day: 'Mon', 
      type: 'Easy Run', 
      distance: '5km', 
      status: 'completed',
      duration: '30 min',
      pace: '6:00/km',
      intensity: 'low',
      heartRateZone: 'Zone 2',
      notes: 'Morning recovery run'
    },
    { 
      id: '2', 
      day: 'Tue', 
      type: 'Rest', 
      distance: '', 
      status: 'rest',
      notes: 'Active recovery - light stretching'
    },
    { 
      id: '3', 
      day: 'Wed', 
      type: 'Tempo Run', 
      distance: '8km', 
      status: 'pending',
      duration: '45 min',
      pace: '5:30/km',
      intensity: 'high',
      heartRateZone: 'Zone 4',
      notes: 'Include 10 min warm-up'
    },
    { 
      id: '4', 
      day: 'Thu', 
      type: 'Easy Run', 
      distance: '5km', 
      status: 'pending',
      duration: '32 min',
      pace: '6:20/km',
      intensity: 'low',
      heartRateZone: 'Zone 2'
    },
    { 
      id: '5', 
      day: 'Fri', 
      type: 'Long Run', 
      distance: '15km', 
      status: 'pending',
      duration: '90 min',
      pace: '6:00/km',
      intensity: 'moderate',
      heartRateZone: 'Zone 3',
      notes: 'Bring water and fuel'
    },
    { 
      id: '6', 
      day: 'Sat', 
      type: 'Easy Run', 
      distance: '6km', 
      status: 'pending',
      duration: '36 min',
      pace: '6:00/km',
      intensity: 'low',
      heartRateZone: 'Zone 2'
    },
    { 
      id: '7', 
      day: 'Sun', 
      type: 'Rest', 
      distance: '', 
      status: 'rest',
      notes: 'Complete rest day'
    },
  ]);

  const completedWorkouts = workouts.filter(w => w.status === 'completed').length;
  const totalWorkouts = workouts.filter(w => w.status !== 'rest').length;

  const toggleWorkoutStatus = (id: string) => {
    setWorkouts(workouts.map(workout => {
      if (workout.id === id && workout.status !== 'rest') {
        return {
          ...workout,
          status: workout.status === 'completed' ? 'pending' : 'completed'
        };
      }
      return workout;
    }));
  };

  const handleEdit = (id: string) => {
    // Placeholder for edit functionality
    console.log('Edit workout:', id);
  };

  return (
    <div className="max-w-full mx-auto p-6">
      <div className="bg-white rounded-lg shadow-sm border border-[#8eb19d]">
        {/* Header */}
        <div className="p-6 border-b border-[#8eb19d]">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-semibold text-[#1e1b18]">
              {viewMode === 'week' ? 'Your Week Ahead' : 'Your Month Ahead'}
            </h1>
            <div className="flex items-center gap-2">
              <button 
                onClick={() => setViewMode(viewMode === 'week' ? 'month' : 'week')}
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
              <button className="p-2 border border-[#8eb19d] text-[#1e1b18] rounded-lg hover:bg-[#eacdc2]">
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button className="p-2 border border-[#8eb19d] text-[#1e1b18] rounded-lg hover:bg-[#eacdc2]">
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
          <div className="text-sm text-[#1e1b18]">
            Progress: <span className="font-medium text-[#072ac8]">{completedWorkouts}/{totalWorkouts}</span> workouts completed
          </div>
        </div>

        {/* View Content */}
        {viewMode === 'week' ? (
          <div className="p-6 overflow-x-auto">
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
          </div>
        ) : (
          <MonthView 
            workouts={workouts}
            onToggle={toggleWorkoutStatus}
            onEdit={handleEdit}
          />
        )}
      </div>
    </div>
  );
}