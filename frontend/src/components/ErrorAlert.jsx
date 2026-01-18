import React from 'react';
import { AlertCircle, RefreshCw, X } from 'lucide-react';

/**
 * Reusable error alert component with optional retry functionality
 */
export function ErrorAlert({
  message,
  onRetry = null,
  onDismiss = null,
  className = ''
}) {
  // Map common error messages to user-friendly versions
  const getUserFriendlyMessage = (msg) => {
    const errorMap = {
      'Network Error': 'Unable to connect to the server. Please check your internet connection.',
      'Request failed with status code 500': 'Something went wrong on our end. Please try again.',
      'Request failed with status code 401': 'Your session has expired. Please reconnect.',
      'Request failed with status code 403': 'You do not have permission to perform this action.',
      'Request failed with status code 404': 'The requested resource was not found.',
      'timeout': 'The request took too long. Please try again.',
    };

    // Check for partial matches
    for (const [key, value] of Object.entries(errorMap)) {
      if (msg.toLowerCase().includes(key.toLowerCase())) {
        return value;
      }
    }

    return msg;
  };

  const friendlyMessage = getUserFriendlyMessage(message);

  return (
    <div className={`p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3 ${className}`}>
      <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <p className="text-sm text-red-800">{friendlyMessage}</p>
      </div>
      <div className="flex items-center gap-2">
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center gap-1 text-sm text-red-600 hover:text-red-800 font-medium transition-colors"
            aria-label="Retry"
          >
            <RefreshCw className="w-4 h-4" />
            Retry
          </button>
        )}
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="p-1 text-red-400 hover:text-red-600 transition-colors rounded"
            aria-label="Dismiss"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}

export default ErrorAlert;
