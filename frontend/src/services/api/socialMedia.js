import { apiRequest, API_BASE_URL } from './core';

export const socialMedia = {
  listAccounts: (projectId) => apiRequest(`/api/v1/social/${projectId}/accounts`),
  getAccounts: (projectId) => apiRequest(`/api/v1/social/${projectId}/accounts`),
  getFeed: (projectId) => apiRequest(`/api/v1/social/${projectId}/feed?limit=20`),
  getStats: (projectId) => apiRequest(`/api/v1/social/${projectId}/stats`),
  listFeed: (projectId, params) => {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/api/v1/social/${projectId}/feed?${query}`);
  },
  listComments: (projectId, params) => {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/api/v1/social/${projectId}/comments?${query}`);
  },
  generateResponse: (projectId, commentId, data = {}) => {
    return apiRequest(`/api/v1/social/${projectId}/comments/${commentId}/generate-response`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  sendResponse: (projectId, commentId, text) => {
    return apiRequest(`/api/v1/social/${projectId}/comments/${commentId}/send-response`, {
      method: 'POST',
      body: JSON.stringify({ response_text: text }),
    });
  },
};
