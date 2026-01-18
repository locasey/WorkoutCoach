import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';
import './Toast.css';

// Context for toast notifications
const ToastContext = createContext(null);

// Hook to use toast notifications
export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

// Individual Toast component
function Toast({ id, type, message, action, onDismiss }) {
  const icons = {
    success: <CheckCircle className="toast-icon" size={20} />,
    error: <XCircle className="toast-icon" size={20} />,
    warning: <AlertTriangle className="toast-icon" size={20} />,
    info: <Info className="toast-icon" size={20} />,
  };

  return (
    <div className={`toast toast-${type}`} role="alert" aria-live="polite">
      {icons[type]}
      <span className="toast-message">{message}</span>
      {action && (
        <button
          className="toast-action"
          onClick={() => {
            action.onClick();
            onDismiss(id);
          }}
          aria-label={action.label}
        >
          {action.label}
        </button>
      )}
      <button
        className="toast-dismiss"
        onClick={() => onDismiss(id)}
        aria-label="Dismiss notification"
      >
        <X size={16} />
      </button>
    </div>
  );
}

// Toast Container - renders all active toasts
function ToastContainer({ toasts, onDismiss }) {
  if (toasts.length === 0) return null;

  return (
    <div className="toast-container" aria-label="Notifications">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          id={toast.id}
          type={toast.type}
          message={toast.message}
          action={toast.action}
          onDismiss={onDismiss}
        />
      ))}
    </div>
  );
}

// Toast Provider - wraps app and provides toast context
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info', duration = 5000, action = null) => {
    const id = Date.now() + Math.random();

    setToasts((prev) => [...prev, { id, message, type, action }]);

    // Auto-dismiss after duration
    if (duration > 0) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((toast) => toast.id !== id));
      }, duration);
    }

    return id;
  }, []);

  const dismissToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  // Convenience methods for different toast types
  const toast = useCallback({
    success: (message, duration, action) => addToast(message, 'success', duration, action),
    error: (message, duration) => addToast(message, 'error', duration ?? 8000), // Errors stay longer
    warning: (message, duration, action) => addToast(message, 'warning', duration, action),
    info: (message, duration, action) => addToast(message, 'info', duration, action),
  }, [addToast]);

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </ToastContext.Provider>
  );
}

export default Toast;
