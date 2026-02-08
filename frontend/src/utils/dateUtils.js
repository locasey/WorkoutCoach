/**
 * Shared date formatting utilities.
 */

/**
 * Parse a YYYY-MM-DD string as local midnight (not UTC).
 * new Date("2026-02-02") = UTC midnight = previous day in US timezones.
 * This function avoids that by appending T00:00:00.
 * @param {string} dateStr - ISO date string (YYYY-MM-DD)
 * @returns {Date}
 */
export function parseLocalDate(dateStr) {
  if (!dateStr) return new Date(NaN)
  return new Date(dateStr + 'T00:00:00')
}

/**
 * Formats a date string for display (e.g. "Jan 15, 2026").
 * @param {string | null | undefined} dateString - ISO date string or null/undefined
 * @returns {string} Formatted date or 'N/A' if invalid
 */
export function formatDate(dateString) {
  if (!dateString) return 'N/A';
  const date = parseLocalDate(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}
