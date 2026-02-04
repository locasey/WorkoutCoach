import React from 'react';
import { PlanCard } from './PlanCard';

/**
 * PlanList - Renders a grid of plan cards.
 *
 * Shows all workout plans with actions for each.
 * The active plan is highlighted and has a "Manage" action.
 */
export function PlanList({
  plans,
  activePlanId,
  onActivate,
  onExport,
  onDelete,
  onUpdateName,
  onManage
}) {
  if (plans.length === 0) {
    return (
      <div className="empty-state">
        <p>No workout plans yet. Create one through the Coach chat interface!</p>
      </div>
    );
  }

  return (
    <div className="plan-list">
      {plans.map((plan) => (
        <PlanCard
          key={plan.id}
          plan={plan}
          isActive={plan.id === activePlanId}
          onActivate={onActivate}
          onExport={onExport}
          onDelete={onDelete}
          onUpdateName={onUpdateName}
          onManage={onManage}
        />
      ))}
    </div>
  );
}
