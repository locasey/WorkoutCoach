import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Save, AlertCircle, Check, Trash2 } from 'lucide-react';
import { ConfirmModal } from './ConfirmModal';
import { useToast } from './Toast';
import { WORKOUT_TYPES } from '../utils/workoutMapper';
import { kmToMi, miToKm } from '../utils/workoutMapper';
import './WorkoutEditModal.css';

const API_BASE_URL = '/api';

export function WorkoutEditModal({ workout, isOpen, onClose, onSave, onDelete, unit = 'mi' }) {
  const [formData, setFormData] = useState({
    type: '',
    distance: '',
    duration_minutes: '',
    pace: '',
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const toast = useToast();

  // Initialize form data when workout changes
  useEffect(() => {
    if (workout?._original) {
      const original = workout._original;
      const displayDistance = original.distance_km != null && original.distance_km !== ''
        ? (unit === 'mi' ? kmToMi(original.distance_km) : original.distance_km)
        : '';
      setFormData({
        type: original.type || '',
        distance: displayDistance,
        duration_minutes: original.duration_minutes ?? '',
        pace: original.pace || '',
        notes: original.notes || ''
      });
      setHasChanges(false);
      setError(null);
      setShowDeleteConfirm(false);
    }
  }, [workout, unit]);

  // Track changes
  useEffect(() => {
    if (workout?._original) {
      const original = workout._original;
      const originalDisplayDist = original.distance_km != null && original.distance_km !== ''
        ? (unit === 'mi' ? kmToMi(original.distance_km) : original.distance_km)
        : '';
      const changed =
        formData.type !== (original.type || '') ||
        formData.distance !== originalDisplayDist ||
        formData.duration_minutes !== (original.duration_minutes ?? '') ||
        formData.pace !== (original.pace || '') ||
        formData.notes !== (original.notes || '');
      setHasChanges(changed);
    }
  }, [formData, workout, unit]);

  // Handle Escape key to close modal
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        handleClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, hasChanges]);

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
    if (formData.distance !== '' && formData.distance !== null) {
      const distance = parseFloat(formData.distance);
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

    setLoading(true);
    setError(null);

    try {
      // Prepare update data - only include changed fields
      const updateData = {};
      const original = workout._original;

      if (formData.type !== original.type) {
        updateData.type = formData.type;
      }
      const originalDisplayDist = original.distance_km != null && original.distance_km !== ''
        ? (unit === 'mi' ? kmToMi(original.distance_km) : original.distance_km)
        : '';
      if (formData.distance !== originalDisplayDist) {
        if (formData.distance === '' || formData.distance === null) {
          updateData.distance_km = null;
        } else {
          const val = parseFloat(formData.distance);
          updateData.distance_km = unit === 'mi' ? miToKm(val) : val;
        }
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
        toast.success('Workout updated successfully!');
      }

      onClose();
    } catch (err) {
      console.error('Error updating workout:', err);
      setError(err.response?.data?.error || 'Failed to update workout');
      toast.error('Failed to update workout');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (hasChanges) {
      if (window.confirm('You have unsaved changes. Discard them?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  if (!isOpen || !workout) return null;

  return (
    <>
      <div className="modal-backdrop" onClick={handleClose} />
      <div className="modal-container">
        <div className="md:hidden bottom-sheet-handle" />
        
        <div className="modal-header">
          <h2>
            Edit Workout
            {/* LOC-22: Show slot indicator when workout is part of multi-workout day */}
            {workout.slot && (
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({workout.slot === 1 ? 'AM Session' : 'PM Session'})
              </span>
            )}
          </h2>
          <button onClick={handleClose} className="p-2 text-gray-400 hover:text-black">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="modal-body">
          {error && (
            <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm mb-4">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form id="edit-workout-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Workout Type</label>
              <select
                name="type"
                value={formData.type}
                onChange={handleInputChange}
                className="form-select"
              >
                <option value="">Select a type</option>
                {WORKOUT_TYPES.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex gap-4">
              <div className="form-group flex-1">
                <label className="form-label">Duration (min)</label>
                <input
                  type="number"
                  name="duration_minutes"
                  value={formData.duration_minutes}
                  onChange={handleInputChange}
                  placeholder="45"
                  className="form-input"
                />
              </div>
              <div className="form-group flex-1">
                <label className="form-label">Distance ({unit === 'km' ? 'km' : 'mi'})</label>
                <input
                  type="number"
                  name="distance"
                  value={formData.distance}
                  onChange={handleInputChange}
                  placeholder={unit === 'km' ? '10' : '6.2'}
                  step="0.1"
                  className="form-input"
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Pace</label>
              <input
                type="text"
                name="pace"
                value={formData.pace}
                onChange={handleInputChange}
                placeholder="5:30/km"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Notes</label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                rows={3}
                placeholder="Target Zone 2 heart rate..."
                className="form-textarea resize-none"
              />
            </div>
          </form>
        </div>

        <div className="modal-footer">
          {onDelete && (
            <button
              type="button"
              onClick={() => setShowDeleteConfirm(true)}
              className="btn-modal"
              style={{ color: '#dc2626', borderColor: '#dc2626', marginRight: 'auto' }}
            >
              <Trash2 className="w-4 h-4" style={{ marginRight: 4, display: 'inline' }} />
              Delete
            </button>
          )}
          <button
            type="button"
            onClick={handleClose}
            className="btn-modal btn-modal-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            form="edit-workout-form"
            className="btn-modal btn-modal-primary"
            disabled={loading || !hasChanges}
          >
            {loading ? 'Saving...' : 'Save Workout'}
          </button>
        </div>
      </div>

      <ConfirmModal
        isOpen={showDeleteConfirm}
        variant="danger"
        title="Delete Workout"
        message="This workout will be permanently removed."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        onConfirm={() => {
          onDelete(workout.id);
          setShowDeleteConfirm(false);
        }}
        onCancel={() => setShowDeleteConfirm(false)}
      />
    </>
  );
}
