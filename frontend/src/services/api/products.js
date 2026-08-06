import { apiRequest, API_BASE_URL } from './core';

export const products = {
  list: async (projectId) => {
    return apiRequest(`/api/v1/products/${projectId}`);
  },

  get: async (projectId, productId) => {
    return apiRequest(`/api/v1/products/${projectId}/${productId}`);
  },

  create: async (projectId, data) => {
    return apiRequest(`/api/v1/products/${projectId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  update: async (projectId, productId, data) => {
    return apiRequest(`/api/v1/products/${projectId}/${productId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  delete: async (projectId, productId) => {
    return apiRequest(`/api/v1/products/${projectId}/${productId}`, {
      method: 'DELETE',
    });
  },

  uploadImage: async (projectId, productId, formData) => {
    // Note: formData should be passed directly as body
    // fetch will automatically set Content-Type to multipart/form-data with boundary
    // customized to NOT set Content-Type header manually if it's FormData
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/api/v1/products/${projectId}/${productId}/images`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: formData,
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        window.location.replace('/login');
        throw new Error('Authentication required');
      }
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return response.json();
  },

  deleteImage: async (projectId, productId, index) => {
    return apiRequest(`/api/v1/products/${projectId}/${productId}/images/${index}`, {
      method: 'DELETE',
    });
  },

  updateImage: async (projectId, productId, index, data) => {
    return apiRequest(`/api/v1/products/${projectId}/${productId}/images/${index}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  reorderImages: async (projectId, productId, images) => {
    return apiRequest(`/api/v1/products/${projectId}/${productId}/images`, {
      method: 'PUT',
      body: JSON.stringify({ images }),
    });
  },

  bulkUpload: async (projectId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    return apiRequest(`/api/v1/products/${projectId}/bulk-upload`, {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set content-type for FormData
    });
  },
};
