/**
 * Shared date formatting utilities.
 */

/**
 * Formats a date string for display (e.g. "Jan 15, 2026").
 * @param {string | null | undefined} dateString - ISO date string or null/undefined
 * @returns {string} Formatted date or 'N/A' if invalid
 */
export function formatDate(dateString) {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}
