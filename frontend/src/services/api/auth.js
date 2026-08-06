import { apiRequest, API_BASE_URL } from './core';

export const auth = {
  login: async (data) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }

    const result = await response.json();

    // Store the access token if provided
    if (result.access_token) {
      localStorage.setItem('access_token', result.access_token);
    }

    return result;
  },

  getCurrentUser: async () => {
    return apiRequest('/api/v1/auth/me');
  },

  logout: async () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};
