/**
 * API Service for AI Sales Commander
 * Complete implementation with all endpoints
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

// Helper function to get auth token
const getAuthToken = () => {
  const token = localStorage.getItem('access_token');
  console.log('[DEBUG] getAuthToken:', token ? 'Token exists' : 'No token');
  return token;
};

// Helper function for API requests
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

  if (!response.ok) {
    // Handle 401 Unauthorized - redirect to login
    if (response.status === 401) {
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.replace('/login');
      }
      throw new Error('Authentication required. Please log in again.');
    }

    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export { apiRequest, API_BASE_URL, getAuthToken };
