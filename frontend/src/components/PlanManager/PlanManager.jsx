import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PlanList } from './PlanList';
import { PlanUpload } from './PlanUpload';
import { ActivePlanView } from './ActivePlanView';
import { ConfirmModal } from '../ConfirmModal';
import { useToast } from '../Toast';
import { ErrorAlert } from '../ErrorAlert';
import { ArrowLeft, List, Settings2 } from 'lucide-react';
import './PlanManager.css';

const API_BASE_URL = '/api';

/**
 * PlanManager - Two-level view for managing workout plans.
 *
 * Level 1 (Default): Manage Active Plan – active plan detail + upload
 * Level 2: All Plans – grid of all plans; enter via "Manage All Plans" button
 */
export function PlanManager() {
  const [plans, setPlans] = useState([]);
  const [activePlanId, setActivePlanId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // View state: 'manage' (active plan first) or 'landing' (all plans grid)
  const [view, setView] = useState('manage');
  // Delete confirmation: planId when modal is open, null otherwise
  const [deleteConfirmPlanId, setDeleteConfirmPlanId] = useState(null);
  const toast = useToast();

  // Fetch all workout plans
  const fetchPlans = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_BASE_URL}/workout-plans`);
      const plansData = response.data.plans || [];

      setPlans(plansData);

      // Find active plan
      const active = plansData.find(p => p.is_active);
      if (active) {
        setActivePlanId(active.id);
      } else {
        setActivePlanId(null);
      }
    } catch (err) {
      console.error('Error fetching plans:', err);
      setError(err.response?.data?.error || 'Failed to load workout plans');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlans();
  }, []);

  // Activate a plan
  const handleActivate = async (planId) => {
    try {
      await axios.post(`${API_BASE_URL}/workout-plans/${planId}/activate`);
      setActivePlanId(planId);
      toast.success('Plan activated successfully!');
      fetchPlans();
    } catch (err) {
      console.error('Error activating plan:', err);
      toast.error(err.response?.data?.error || 'Failed to activate plan');
    }
  };

  // Export a plan to Excel
  const handleExport = async (planId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/export/excel/${planId}`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `workout_plan_${planId}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Workout plan exported successfully!');
    } catch (err) {
      console.error('Error exporting plan:', err);
      toast.error(err.response?.data?.error || 'Failed to export plan');
    }
  };

  // Request delete confirmation (opens modal)
  const handleDeleteRequest = (planId) => {
    if (planId === activePlanId) {
      toast.warning('Cannot delete the active plan. Please activate another plan first.');
      return;
    }
    setDeleteConfirmPlanId(planId);
  };

  // Delete a plan with optimistic update (called after modal confirm)
  const handleDelete = async (planId) => {
    setDeleteConfirmPlanId(null);

    // Store the plan in case we need to restore it
    const deletedPlan = plans.find(p => p.id === planId);

    // Optimistically remove from UI immediately
    setPlans(prevPlans => prevPlans.filter(p => p.id !== planId));

    try {
      await axios.delete(`${API_BASE_URL}/workout-plans/${planId}`);
      toast.success('Plan deleted successfully');
    } catch (err) {
      console.error('Error deleting plan:', err);

      // Restore the plan on error
      if (deletedPlan) {
        setPlans(prevPlans => [...prevPlans, deletedPlan].sort((a, b) =>
          new Date(b.created_at) - new Date(a.created_at)
        ));
      }

      toast.error(err.response?.data?.error || 'Failed to delete plan');
    }
  };

  // Update plan name
  const handleUpdateName = async (planId, newName) => {
    try {
      const response = await axios.patch(`${API_BASE_URL}/workout-plans/${planId}`, {
        name: newName
      });
      // Update local state
      setPlans(prevPlans =>
        prevPlans.map(p =>
          p.id === planId ? { ...p, name: response.data.plan.name } : p
        )
      );
      toast.success('Plan name updated!');
      return true;
    } catch (err) {
      console.error('Error updating plan name:', err);
      toast.error(err.response?.data?.error || 'Failed to update plan name');
      return false;
    }
  };

  // Handle file upload (UI only - backend parsing not implemented yet)
  const handleFileUpload = (file) => {
    toast.info(`File "${file.name}" selected. Backend parsing coming soon!`);
  };

  // Navigate to Manage Active Plan (default view)
  const handleShowActivePlan = () => {
    setView('manage');
  };

  // Navigate to All Plans grid
  const handleShowAllPlans = () => {
    setView('landing');
  };

  // Get the active plan object
  const activePlan = plans.find(p => p.id === activePlanId);

  if (loading) {
    return (
      <div className="plan-manager">
        <h2>Manage Active Plan</h2>
        <p className="description">Loading your workout plans...</p>
      </div>
    );
  }

  // Default view: Manage Active Plan (active plan + upload)
  if (view === 'manage') {
    return (
      <div className="plan-manager">
        <div className="plan-manager-header">
          <h2>Manage Active Plan</h2>
          <p className="description">
            Configure your active training plan, upload a new plan, or export your schedule.
          </p>
          <button className="manage-all-plans-button" onClick={handleShowAllPlans}>
            <List className="w-5 h-5" />
            <span>Manage All Plans</span>
          </button>
        </div>

        {error && (
          <ErrorAlert
            message={error}
            onRetry={fetchPlans}
            onDismiss={() => setError(null)}
          />
        )}

        {activePlan ? (
          <ActivePlanView
            plan={activePlan}
            onExport={handleExport}
            onDelete={handleDeleteRequest}
            onUpdateName={handleUpdateName}
          />
        ) : (
          <div className="no-active-plan">
            <Settings2 className="w-12 h-12" />
            <h3>No Active Plan</h3>
            <p>Activate a plan from your plan list to manage it here.</p>
            <button className="btn-secondary" onClick={handleShowAllPlans}>
              Manage All Plans
            </button>
          </div>
        )}

        <PlanUpload onUpload={handleFileUpload} />

        <ConfirmModal
          isOpen={!!deleteConfirmPlanId}
          title="Delete plan?"
          message="Are you sure you want to delete this plan? This action cannot be undone."
          confirmLabel="Delete"
          cancelLabel="Cancel"
          variant="danger"
          onConfirm={() => deleteConfirmPlanId && handleDelete(deleteConfirmPlanId)}
          onCancel={() => setDeleteConfirmPlanId(null)}
        />
      </div>
    );
  }

  // All Plans view: Grid of all plans (entered via "Manage All Plans")
  return (
    <div className="plan-manager">
      <div className="plan-manager-header">
        <button className="back-button" onClick={handleShowActivePlan}>
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Active Plan</span>
        </button>
        <h2>All Plans</h2>
        <p className="description">
          View and manage all your workout plans. The active plan is shown in your Week Ahead view.
        </p>
      </div>

      {error && (
        <ErrorAlert
          message={error}
          onRetry={fetchPlans}
          onDismiss={() => setError(null)}
        />
      )}

      <PlanList
        plans={plans}
        activePlanId={activePlanId}
        onActivate={handleActivate}
        onExport={handleExport}
        onDelete={handleDeleteRequest}
        onUpdateName={handleUpdateName}
        onManage={handleShowActivePlan}
      />

      <ConfirmModal
        isOpen={!!deleteConfirmPlanId}
        title="Delete plan?"
        message="Are you sure you want to delete this plan? This action cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        variant="danger"
        onConfirm={() => deleteConfirmPlanId && handleDelete(deleteConfirmPlanId)}
        onCancel={() => setDeleteConfirmPlanId(null)}
      />
    </div>
  );
}
