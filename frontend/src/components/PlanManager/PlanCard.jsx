import React from 'react';
import { Calendar, FileText, CheckCircle, Download, Trash2 } from 'lucide-react';

export function PlanCard({ plan, isActive, onActivate, onExport, onDelete }) {
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
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
        <h3 className="plan-title">{plan.plan_name || 'Untitled Plan'}</h3>
        <p className="plan-goal">{plan.goal || 'No goal specified'}</p>
        
        <div className="plan-meta">
          <div className="plan-meta-item">
            <Calendar className="w-4 h-4" />
            <span>Started: {formatDate(plan.created_at)}</span>
          </div>
          <div className="plan-meta-item">
            <FileText className="w-4 h-4" />
            <span>{plan.workout_count || 0} workouts</span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="plan-card-actions">
        {!isActive && (
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
