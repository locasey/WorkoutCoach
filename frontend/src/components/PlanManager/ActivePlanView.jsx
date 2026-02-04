import React, { useState } from 'react';
import { Calendar, FileText, CheckCircle, Download, Trash2, Pencil, Check, X } from 'lucide-react';
import { formatDate } from '../../utils/dateUtils';

/**
 * ActivePlanView - Displays the active plan with prominent actions.
 *
 * This component is shown in the "Manage" view of PlanManager.
 * It provides:
 * - Editable plan name
 * - Plan details (goal, duration, dates)
 * - Export and delete actions
 */
export function ActivePlanView({ plan, onExport, onDelete, onUpdateName }) {
  const [isEditingName, setIsEditingName] = useState(false);
  const [editedName, setEditedName] = useState(plan.name || '');

  // Display name with fallback to goal
  const displayName = plan.name || plan.goal?.substring(0, 50) || 'Untitled Plan';

  // Handle name edit save
  const handleSaveName = async () => {
    if (editedName.trim() && editedName !== plan.name) {
      const success = await onUpdateName(plan.id, editedName.trim());
      if (success) {
        setIsEditingName(false);
      }
    } else {
      setIsEditingName(false);
      setEditedName(plan.name || '');
    }
  };

  // Handle cancel edit
  const handleCancelEdit = () => {
    setIsEditingName(false);
    setEditedName(plan.name || '');
  };

  // Handle key press in name input
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSaveName();
    } else if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  return (
    <div className="active-plan-view">
      {/* Plan Header with Active Badge */}
      <div className="active-plan-header">
        <div className="active-badge large">
          <CheckCircle className="w-5 h-5" />
          Active Plan
        </div>
        <div className="duration-badge large">
          {plan.duration_weeks} weeks
        </div>
      </div>

      {/* Editable Plan Name */}
      <div className="active-plan-name-section">
        {isEditingName ? (
          <div className="name-edit-container">
            <input
              type="text"
              className="name-edit-input"
              value={editedName}
              onChange={(e) => setEditedName(e.target.value)}
              onKeyDown={handleKeyDown}
              maxLength={255}
              autoFocus
              placeholder="Enter plan name..."
            />
            <div className="name-edit-actions">
              <button
                className="name-edit-btn save"
                onClick={handleSaveName}
                title="Save"
              >
                <Check className="w-4 h-4" />
              </button>
              <button
                className="name-edit-btn cancel"
                onClick={handleCancelEdit}
                title="Cancel"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        ) : (
          <div className="name-display-container">
            <h3 className="active-plan-title">{displayName}</h3>
            <button
              className="name-edit-trigger"
              onClick={() => {
                setEditedName(plan.name || displayName);
                setIsEditingName(true);
              }}
              title="Edit plan name"
            >
              <Pencil className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Plan Goal (if different from name) */}
      {plan.goal && plan.goal !== plan.name && (
        <p className="active-plan-goal">{plan.goal}</p>
      )}

      {/* Plan Metadata */}
      <div className="active-plan-meta">
        <div className="meta-item">
          <Calendar className="w-5 h-5" />
          <div>
            <span className="meta-label">Started</span>
            <span className="meta-value">{formatDate(plan.start_date || plan.created_at)}</span>
          </div>
        </div>
        <div className="meta-item">
          <FileText className="w-5 h-5" />
          <div>
            <span className="meta-label">Workouts</span>
            <span className="meta-value">{plan.workout_count || 0} scheduled</span>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="active-plan-actions">
        <button
          className="btn-primary"
          onClick={() => onExport(plan.id)}
        >
          <Download className="w-5 h-5" />
          Export to Excel
        </button>
        <button
          className="btn-danger"
          onClick={() => onDelete(plan.id)}
          disabled={true}
          title="Cannot delete active plan"
        >
          <Trash2 className="w-5 h-5" />
          Delete Plan
        </button>
      </div>
      <p className="action-hint">
        To delete this plan, first activate a different plan.
      </p>
    </div>
  );
}
