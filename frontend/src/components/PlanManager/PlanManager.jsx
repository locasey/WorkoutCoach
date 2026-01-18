import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PlanList } from './PlanList';
import { PlanUpload } from './PlanUpload';
import { useToast } from '../Toast';
import { ErrorAlert } from '../ErrorAlert';
import './PlanManager.css';

const API_BASE_URL = '/api';

export function PlanManager() {
  const [plans, setPlans] = useState([]);
  const [activePlanId, setActivePlanId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
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
      fetchPlans(); // Refresh to get updated data
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

  // Delete a plan with optimistic update
  const handleDelete = async (planId) => {
    // Prevent deleting active plan
    if (planId === activePlanId) {
      toast.warning('Cannot delete the active plan. Please activate another plan first.');
      return;
    }

    if (!window.confirm('Are you sure you want to delete this plan? This action cannot be undone.')) {
      return;
    }

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

  // Handle file upload (UI only - backend parsing not implemented yet)
  const handleFileUpload = (file) => {
    toast.info(`File "${file.name}" selected. Backend parsing coming soon!`);
  };

  if (loading) {
    return (
      <div className="plan-manager">
        <h2>My Plans</h2>
        <p className="description">Loading your workout plans...</p>
      </div>
    );
  }

  return (
    <div className="plan-manager">
      <div className="plan-manager-header">
        <h2>My Plans</h2>
        <p className="description">
          View, manage, and upload your workout plans. The active plan is shown in your Week Ahead view.
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
        onDelete={handleDelete}
      />

      <PlanUpload onUpload={handleFileUpload} />
    </div>
  );
}
