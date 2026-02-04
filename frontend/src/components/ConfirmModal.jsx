import React, { useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';
import './ConfirmModal.css';

/**
 * ConfirmModal - Reusable confirmation dialog.
 *
 * Replaces window.confirm for consistent UX (accessible, styled).
 * Props: isOpen, title, message, confirmLabel, cancelLabel, onConfirm, onCancel, variant ('danger' | 'default')
 */
export function ConfirmModal({
  isOpen,
  title = 'Confirm',
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  onConfirm,
  onCancel,
  variant = 'default'
}) {
  // Close on Escape
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onCancel?.();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) onCancel?.();
  };

  return (
    <div className="confirm-modal-backdrop" onClick={handleBackdropClick}>
      <div className="confirm-modal-container" role="dialog" aria-modal="true" aria-labelledby="confirm-modal-title">
        <div className="confirm-modal-header">
          {variant === 'danger' && <AlertTriangle className="confirm-modal-icon confirm-modal-icon--danger" />}
          <h2 id="confirm-modal-title" className="confirm-modal-title">{title}</h2>
        </div>
        <div className="confirm-modal-body">
          <p className="confirm-modal-message">{message}</p>
        </div>
        <div className="confirm-modal-footer">
          <button type="button" className="confirm-modal-btn confirm-modal-btn--secondary" onClick={onCancel}>
            {cancelLabel}
          </button>
          <button
            type="button"
            className={`confirm-modal-btn confirm-modal-btn--primary ${variant === 'danger' ? 'confirm-modal-btn--danger' : ''}`}
            onClick={onConfirm}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
