import React from 'react';
import { PlanCard } from './PlanCard';

export function PlanList({ plans, activePlanId, onActivate, onExport, onDelete }) {
  if (plans.length === 0) {
    return (
      <div className="empty-state">
        <p>No workout plans yet. Create one through the Chat interface!</p>
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
        />
      ))}
    </div>
  );
}
