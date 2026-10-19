/**
 * API Service for AI Sales Commander
 * Complete implementation with all endpoints
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

/** Retrieves the stored JWT access token from localStorage. */
const getAuthToken = () => {
  const token = localStorage.getItem('access_token');
  return token;
};

/**
 * Core fetch wrapper for all API requests.
 * Handles 204 No Content gracefully and maps 404 on DELETE to success.
 *
 * @param {string} endpoint - API path, e.g. "/api/v1/integrations/..."
 * @param {RequestInit} options - fetch options (method, body, etc.)
 * @returns {Promise<any>} Parsed JSON body, or null for empty responses (204/205)
 */
async function apiRequest(endpoint, options = {}) {
  const token = getAuthToken();

  const config = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    ...options,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  // 204 / 205 No Content — success with empty body
  if (response.status === 204 || response.status === 205) {
    return null;
  }

  // 404 on DELETE is idempotent success (already deleted)
  if (response.status === 404 && config.method === 'DELETE') {
    return null;
  }

  if (!response.ok) {
    // 401 Unauthorized — clear session and redirect to login
    if (response.status === 401) {
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.replace('/login');
      }
      throw new Error('Authentication required. Please log in again.');
    }

    const errorBody = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(errorBody.detail || `HTTP ${response.status}`);
  }

  // Parse JSON body for all other success responses
  return response.json().catch(() => null);
}

export { apiRequest, API_BASE_URL, getAuthToken };
