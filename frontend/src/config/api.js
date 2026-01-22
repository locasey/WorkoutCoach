/**
 * API Configuration
 *
 * Provides the base URL for API requests based on environment.
 * In development, requests are proxied through Vite to localhost:5000.
 * In production, VITE_API_URL should point to the backend service.
 */

// Get API URL from environment or default to relative path (uses Vite proxy)
export const API_BASE_URL = import.meta.env.VITE_API_URL || ''

/**
 * Build a full API URL
 *
 * @param {string} path - The API path (e.g., '/api/auth/login')
 * @returns {string} Full URL with base URL prepended
 */
export const getApiUrl = (path) => {
  return `${API_BASE_URL}${path}`
}

/**
 * Check if running in production mode
 */
export const isProduction = import.meta.env.PROD
