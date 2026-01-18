import React from 'react';
import { Calendar, MapPin, Clock, Heart, Activity } from 'lucide-react';

export function ActivityCard({ activity, formatDate, formatPace }) {
  return (
    <div className="bg-white border-2 border-[#8eb19d] rounded-lg p-4 shadow-sm">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="font-semibold text-[#1e1b18] text-base mb-1 line-clamp-2">
            {activity.name}
          </h3>
          <div className="inline-flex items-center gap-1 px-2 py-1 bg-[#072ac8]/10 text-[#072ac8] rounded text-xs font-medium">
            <Activity className="w-3 h-3" />
            {activity.activity_type}
          </div>
        </div>
        <div className="ml-2">
          {activity.linked_workout_id ? (
            <span className="inline-block px-2 py-1 bg-[#8eb19d] text-white rounded text-xs font-semibold">
              Linked
            </span>
          ) : (
            <span className="inline-block px-2 py-1 bg-[#a44200]/20 text-[#a44200] rounded text-xs font-semibold">
              Unlinked
            </span>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-3">
        <div className="flex items-center gap-2 text-sm">
          <Calendar className="w-4 h-4 text-[#072ac8]" />
          <div>
            <div className="text-xs text-[#1e1b18]/60">Date</div>
            <div className="font-medium text-[#1e1b18]">
              {formatDate(activity.start_date)}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 text-sm">
          <MapPin className="w-4 h-4 text-[#072ac8]" />
          <div>
            <div className="text-xs text-[#1e1b18]/60">Distance</div>
            <div className="font-medium text-[#1e1b18]">
              {activity.distance_km?.toFixed(2) || '0.00'} km
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 text-sm">
          <Clock className="w-4 h-4 text-[#072ac8]" />
          <div>
            <div className="text-xs text-[#1e1b18]/60">Time</div>
            <div className="font-medium text-[#1e1b18]">
              {Math.round(activity.moving_time_minutes || 0)} min
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 text-sm">
          <Heart className="w-4 h-4 text-[#a44200]" />
          <div>
            <div className="text-xs text-[#1e1b18]/60">Heart Rate</div>
            <div className="font-medium text-[#1e1b18]">
              {activity.average_heartrate ? `${Math.round(activity.average_heartrate)} bpm` : 'N/A'}
            </div>
          </div>
        </div>
      </div>

      {/* Pace - Full Width */}
      {activity.average_speed_kmh && (
        <div className="mt-3 pt-3 border-t border-[#1e1b18]/10">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#1e1b18]/60">Average Pace</span>
            <span className="font-semibold text-[#072ac8]">
              {formatPace(activity.average_speed_kmh)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
