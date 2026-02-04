import React, { useState } from 'react';
import { Calendar, FileText, CheckCircle, Download, Trash2, Pencil, Check, X, Settings2 } from 'lucide-react';
import { formatDate } from '../../utils/dateUtils';

/**
 * PlanCard - Displays a single workout plan as a card.
 *
 * Features:
 * - Shows plan name (with fallback to goal)
 * - Inline name editing
 * - Active badge for the current plan
 * - Actions: Activate, Export, Delete, Manage (for active)
 */
export function PlanCard({
  plan,
  isActive,
  onActivate,
  onExport,
  onDelete,
  onUpdateName,
  onManage
}) {
  const [isEditingName, setIsEditingName] = useState(false);
  const [editedName, setEditedName] = useState(plan.name || '');

  // Display name with fallback to truncated goal
  const displayName = plan.name || (plan.goal ? plan.goal.substring(0, 50) : 'Untitled Plan');

  // Handle save name
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

  // Handle key press
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSaveName();
    } else if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  return (
    <div className={`plan-card ${isActive ? 'active' : ''}`}>
      {/* Header with Badge */}
      <div className="plan-card-header">
        {isActive && (
          <div className="active-badge">
            <CheckCircle className="w-4 h-4" />
            Active Plan
          </div>
        )}
        <div className="duration-badge">
          {plan.duration_weeks} weeks
        </div>
      </div>

      {/* Content */}
      <div className="plan-card-content">
        {/* Editable Title */}
        {isEditingName ? (
          <div className="name-edit-inline">
            <input
              type="text"
              className="name-edit-input-inline"
              value={editedName}
              onChange={(e) => setEditedName(e.target.value)}
              onKeyDown={handleKeyDown}
              maxLength={255}
              autoFocus
              placeholder="Plan name..."
            />
            <button
              className="name-edit-btn-inline save"
              onClick={handleSaveName}
              title="Save"
            >
              <Check className="w-3 h-3" />
            </button>
            <button
              className="name-edit-btn-inline cancel"
              onClick={handleCancelEdit}
              title="Cancel"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        ) : (
          <div className="plan-title-row">
            <h3 className="plan-title">{displayName}</h3>
            <button
              className="name-edit-trigger-inline"
              onClick={() => {
                setEditedName(plan.name || displayName);
                setIsEditingName(true);
              }}
              title="Edit plan name"
            >
              <Pencil className="w-3 h-3" />
            </button>
          </div>
        )}

        {/* Show goal if different from name */}
        {plan.goal && plan.goal !== plan.name && (
          <p className="plan-goal">{plan.goal}</p>
        )}

        <div className="plan-meta">
          <div className="plan-meta-item">
            <Calendar className="w-4 h-4" />
            <span>Started: {formatDate(plan.start_date || plan.created_at)}</span>
          </div>
          <div className="plan-meta-item">
            <FileText className="w-4 h-4" />
            <span>{plan.workout_count || 0} workouts</span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="plan-card-actions">
        {isActive ? (
          <button
            onClick={onManage}
            className="btn-primary"
          >
            <Settings2 className="w-4 h-4" />
            Manage
          </button>
        ) : (
          <button
            onClick={() => onActivate(plan.id)}
            className="btn-secondary"
          >
            Activate
          </button>
        )}
        <button
          onClick={() => onExport(plan.id)}
          className="btn-secondary"
        >
          <Download className="w-4 h-4" />
          Export
        </button>
        <button
          onClick={() => onDelete(plan.id)}
          disabled={isActive}
          className="btn-danger"
          title={isActive ? 'Cannot delete active plan' : 'Delete plan'}
        >
          <Trash2 className="w-4 h-4" />
          Delete
        </button>
      </div>
    </div>
  );
}
