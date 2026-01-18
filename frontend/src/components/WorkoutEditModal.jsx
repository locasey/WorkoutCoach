import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Save, AlertCircle, Check } from 'lucide-react';

const API_BASE_URL = '/api';

// Valid workout types matching backend validation
const WORKOUT_TYPES = [
  { value: 'long_run', label: 'Long Run' },
  { value: 'tempo', label: 'Tempo' },
  { value: 'intervals', label: 'Intervals' },
  { value: 'easy_run', label: 'Easy Run' },
  { value: 'rest', label: 'Rest' },
  { value: 'cross_training', label: 'Cross Training' },
  { value: 'recovery', label: 'Recovery' },
  { value: 'fartlek', label: 'Fartlek' },
  { value: 'hill_repeats', label: 'Hill Repeats' }
];

export function WorkoutEditModal({ workout, isOpen, onClose, onSave }) {
  const [formData, setFormData] = useState({
    type: '',
    distance_km: '',
    duration_minutes: '',
    pace: '',
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Initialize form data when workout changes
  useEffect(() => {
    if (workout?._original) {
      const original = workout._original;
      setFormData({
        type: original.type || '',
        distance_km: original.distance_km ?? '',
        duration_minutes: original.duration_minutes ?? '',
        pace: original.pace || '',
        notes: original.notes || ''
      });
      setHasChanges(false);
      setError(null);
    }
  }, [workout]);

  // Track changes
  useEffect(() => {
    if (workout?._original) {
      const original = workout._original;
      const changed =
        formData.type !== (original.type || '') ||
        formData.distance_km !== (original.distance_km ?? '') ||
        formData.duration_minutes !== (original.duration_minutes ?? '') ||
        formData.pace !== (original.pace || '') ||
        formData.notes !== (original.notes || '');
      setHasChanges(changed);
    }
  }, [formData, workout]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(null);
  };

  const validateForm = () => {
    const errors = [];

    // Validate type
    if (formData.type && !WORKOUT_TYPES.find(t => t.value === formData.type)) {
      errors.push('Invalid workout type selected');
    }

    // Validate distance
    if (formData.distance_km !== '' && formData.distance_km !== null) {
      const distance = parseFloat(formData.distance_km);
      if (isNaN(distance) || distance < 0) {
        errors.push('Distance must be a non-negative number');
      }
    }

    // Validate duration
    if (formData.duration_minutes !== '' && formData.duration_minutes !== null) {
      const duration = parseInt(formData.duration_minutes);
      if (isNaN(duration) || duration < 0) {
        errors.push('Duration must be a non-negative whole number');
      }
    }

    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate
    const validationErrors = validateForm();
    if (validationErrors.length > 0) {
      setError(validationErrors.join('. '));
      return;
    }

    // Show confirmation if there are changes
    if (hasChanges) {
      setShowConfirmation(true);
      return;
    }

    // No changes, just close
    onClose();
  };

  const handleConfirmedSave = async () => {
    setShowConfirmation(false);
    setLoading(true);
    setError(null);

    try {
      // Prepare update data - only include changed fields
      const updateData = {};
      const original = workout._original;

      if (formData.type !== original.type) {
        updateData.type = formData.type;
      }
      if (formData.distance_km !== (original.distance_km ?? '')) {
        updateData.distance_km = formData.distance_km === '' ? null : parseFloat(formData.distance_km);
      }
      if (formData.duration_minutes !== (original.duration_minutes ?? '')) {
        updateData.duration_minutes = formData.duration_minutes === '' ? null : parseInt(formData.duration_minutes);
      }
      if (formData.pace !== (original.pace || '')) {
        updateData.pace = formData.pace || null;
      }
      if (formData.notes !== (original.notes || '')) {
        updateData.notes = formData.notes || null;
      }

      // Only update if there are changes
      if (Object.keys(updateData).length > 0) {
        const response = await axios.put(`${API_BASE_URL}/workouts/${workout.id}`, updateData);
        onSave(response.data.workout);
      }

      onClose();
    } catch (err) {
      console.error('Error updating workout:', err);
      setError(err.response?.data?.error || 'Failed to update workout');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (hasChanges) {
      setShowConfirmation(true);
    } else {
      onClose();
    }
  };

  const handleDiscardChanges = () => {
    setShowConfirmation(false);
    setHasChanges(false);
    onClose();
  };

  if (!isOpen || !workout) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#8eb19d]">
          <h2 className="text-lg font-semibold text-[#1e1b18]">
            Edit Workout - {workout.day}
          </h2>
          <button
            onClick={handleClose}
            className="p-1 text-[#1e1b18]/60 hover:text-[#1e1b18] hover:bg-[#eacdc2] rounded transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {/* Error display */}
          {error && (
            <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Workout Type */}
          <div>
            <label htmlFor="type" className="block text-sm font-medium text-[#1e1b18] mb-1">
              Workout Type
            </label>
            <select
              id="type"
              name="type"
              value={formData.type}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-[#8eb19d] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#072ac8] focus:border-transparent"
            >
              <option value="">Select a type</option>
              {WORKOUT_TYPES.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Distance */}
          <div>
            <label htmlFor="distance_km" className="block text-sm font-medium text-[#1e1b18] mb-1">
              Distance (km)
            </label>
            <input
              type="number"
              id="distance_km"
              name="distance_km"
              value={formData.distance_km}
              onChange={handleInputChange}
              min="0"
              step="0.1"
              placeholder="e.g., 10.5"
              className="w-full px-3 py-2 border border-[#8eb19d] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#072ac8] focus:border-transparent"
            />
          </div>

          {/* Duration */}
          <div>
            <label htmlFor="duration_minutes" className="block text-sm font-medium text-[#1e1b18] mb-1">
              Duration (minutes)
            </label>
            <input
              type="number"
              id="duration_minutes"
              name="duration_minutes"
              value={formData.duration_minutes}
              onChange={handleInputChange}
              min="0"
              step="1"
              placeholder="e.g., 45"
              className="w-full px-3 py-2 border border-[#8eb19d] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#072ac8] focus:border-transparent"
            />
          </div>

          {/* Pace */}
          <div>
            <label htmlFor="pace" className="block text-sm font-medium text-[#1e1b18] mb-1">
              Pace
            </label>
            <input
              type="text"
              id="pace"
              name="pace"
              value={formData.pace}
              onChange={handleInputChange}
              placeholder="e.g., 5:30/km or easy"
              className="w-full px-3 py-2 border border-[#8eb19d] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#072ac8] focus:border-transparent"
            />
          </div>

          {/* Notes */}
          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-[#1e1b18] mb-1">
              Notes
            </label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              rows={3}
              placeholder="Additional notes for this workout..."
              className="w-full px-3 py-2 border border-[#8eb19d] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#072ac8] focus:border-transparent resize-none"
            />
          </div>

          {/* Scheduled Date (read-only) */}
          {workout._original?.scheduled_date && (
            <div className="pt-2 border-t border-[#8eb19d]/30">
              <p className="text-sm text-[#1e1b18]/60">
                Scheduled: {new Date(workout._original.scheduled_date).toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-[#8eb19d]">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 px-4 py-2 border border-[#8eb19d] text-[#1e1b18] rounded-lg hover:bg-[#eacdc2] transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-[#072ac8] text-white rounded-lg hover:bg-[#072ac8]/90 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              disabled={loading || !hasChanges}
            >
              {loading ? (
                <>
                  <span className="animate-spin">...</span>
                  Saving
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Save Changes
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Confirmation Dialog */}
      {showConfirmation && (
        <div className="fixed inset-0 z-60 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/30" />
          <div className="relative bg-white rounded-lg shadow-xl p-6 mx-4 max-w-sm">
            <h3 className="text-lg font-semibold text-[#1e1b18] mb-2">
              {hasChanges ? 'Save Changes?' : 'Unsaved Changes'}
            </h3>
            <p className="text-[#1e1b18]/70 mb-4">
              {hasChanges
                ? 'Are you sure you want to save these changes to the workout?'
                : 'You have unsaved changes. Do you want to discard them?'}
            </p>
            <div className="flex gap-3">
              {hasChanges ? (
                <>
                  <button
                    onClick={() => setShowConfirmation(false)}
                    className="flex-1 px-4 py-2 border border-[#8eb19d] text-[#1e1b18] rounded-lg hover:bg-[#eacdc2] transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleConfirmedSave}
                    className="flex-1 px-4 py-2 bg-[#072ac8] text-white rounded-lg hover:bg-[#072ac8]/90 transition-colors flex items-center justify-center gap-2"
                  >
                    <Check className="w-4 h-4" />
                    Confirm
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => setShowConfirmation(false)}
                    className="flex-1 px-4 py-2 border border-[#8eb19d] text-[#1e1b18] rounded-lg hover:bg-[#eacdc2] transition-colors"
                  >
                    Keep Editing
                  </button>
                  <button
                    onClick={handleDiscardChanges}
                    className="flex-1 px-4 py-2 bg-[#a44200] text-white rounded-lg hover:bg-[#a44200]/90 transition-colors"
                  >
                    Discard
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
