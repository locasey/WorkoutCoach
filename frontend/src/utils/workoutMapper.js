/**
 * Maps database workout data to the design interface format
 */

/**
 * Derive workout status from database fields
 * @param {Object} workout - Workout from database
 * @returns {'completed' | 'rest' | 'pending'}
 */
export function getWorkoutStatus(workout) {
  if (workout.type === 'rest') {
    return 'rest';
  }
  return workout.is_completed ? 'completed' : 'pending';
}

/**
 * Format distance for display
 * @param {number|null} distanceKm - Distance in kilometers
 * @returns {string} Formatted distance (e.g., "5km")
 */
export function formatDistance(distanceKm) {
  if (!distanceKm) return '';
  return `${distanceKm}km`;
}

/**
 * Format duration for display
 * @param {number|null} durationMinutes - Duration in minutes
 * @returns {string} Formatted duration (e.g., "30 min")
 */
export function formatDuration(durationMinutes) {
  if (!durationMinutes) return '';
  return `${durationMinutes} min`;
}

/**
 * Derive intensity from workout type
 * @param {string} workoutType - Type of workout
 * @returns {'low' | 'moderate' | 'high' | undefined}
 */
export function deriveIntensity(workoutType) {
  const type = workoutType?.toLowerCase() || '';
  
  // High intensity workouts
  if (type.includes('tempo') || type.includes('interval') || type.includes('speed')) {
    return 'high';
  }
  
  // Moderate intensity workouts
  if (type.includes('long') || type.includes('moderate')) {
    return 'moderate';
  }
  
  // Low intensity workouts
  if (type.includes('easy') || type.includes('recovery') || type.includes('rest')) {
    return 'low';
  }
  
  // Default to moderate if unknown
  return 'moderate';
}

/**
 * Derive heart rate zone from workout type
 * @param {string} workoutType - Type of workout
 * @returns {string} Heart rate zone (e.g., "Zone 2")
 */
export function deriveHeartRateZone(workoutType) {
  const type = workoutType?.toLowerCase() || '';
  
  // Zone 4-5: High intensity
  if (type.includes('tempo') || type.includes('interval') || type.includes('speed')) {
    return 'Zone 4';
  }
  
  // Zone 3: Moderate intensity
  if (type.includes('long') || type.includes('moderate')) {
    return 'Zone 3';
  }
  
  // Zone 2: Low intensity
  if (type.includes('easy') || type.includes('recovery')) {
    return 'Zone 2';
  }
  
  // Rest days
  if (type.includes('rest')) {
    return 'Rest';
  }
  
  // Default
  return 'Zone 2';
}

/**
 * Get day name from scheduled date
 * @param {string|null} scheduledDate - ISO date string
 * @returns {string} Day name (e.g., "Mon", "Tue")
 */
export function getDayName(scheduledDate) {
  if (!scheduledDate) return '';
  
  const date = new Date(scheduledDate);
  // JavaScript getDay() returns 0-6 (0=Sunday, 1=Monday, ...)
  const dayIndex = date.getDay();
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  return dayNames[dayIndex];
}

/**
 * Get day name from day number (1-7, where 1=Monday)
 * @param {number} day - Day number (1-7)
 * @returns {string} Day name (e.g., "Mon", "Tue")
 */
export function getDayNameFromNumber(day) {
  const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  // day is 1-7, where 1=Monday, so we subtract 1
  return dayNames[day - 1] || '';
}

/**
 * Map database workout to design interface format
 * @param {Object} dbWorkout - Workout from database API
 * @returns {Object} Workout in design format
 */
export function mapWorkoutToDesign(dbWorkout) {
  const status = getWorkoutStatus(dbWorkout);
  
  // Try to get day name from scheduled_date first, fall back to day number
  let dayName = '';
  if (dbWorkout.scheduled_date) {
    dayName = getDayName(dbWorkout.scheduled_date);
  } else if (dbWorkout.day) {
    dayName = getDayNameFromNumber(dbWorkout.day);
  }
  
  return {
    id: dbWorkout.id,
    day: dayName,
    type: formatWorkoutType(dbWorkout.type),
    distance: formatDistance(dbWorkout.distance_km),
    status: status,
    duration: formatDuration(dbWorkout.duration_minutes),
    pace: dbWorkout.pace || '',
    intensity: deriveIntensity(dbWorkout.type),
    heartRateZone: deriveHeartRateZone(dbWorkout.type),
    notes: dbWorkout.notes || '',
    scheduledDate: dbWorkout.scheduled_date || null, // For date-based features like "today" highlighting
    // LOC-22: Slot for multiple workouts per day (null=single, 1=AM, 2=PM)
    slot: dbWorkout.slot || null,
    // Keep original data for editing
    _original: dbWorkout
  };
}

/**
 * Format workout type for display
 * @param {string} type - Database workout type
 * @returns {string} Formatted type (e.g., "Easy Run", "Tempo Run")
 */
function formatWorkoutType(type) {
  if (!type) return '';
  
  // Convert snake_case to Title Case
  return type
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

