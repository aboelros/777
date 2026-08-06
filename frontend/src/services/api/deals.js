import { apiRequest, API_BASE_URL } from './core';

export const deals = {
  getStages: (projectId) => apiRequest(`/api/v1/deals/${projectId}/stages`),
  createStage: (projectId, data) => apiRequest(`/api/v1/deals/${projectId}/stages`, {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  getDeals: (projectId, params) => {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/api/v1/deals/${projectId}/deals?${query}`);
  },
  createDeal: (projectId, data) => apiRequest(`/api/v1/deals/${projectId}/deals`, {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  updateDeal: (projectId, dealId, data) => apiRequest(`/api/v1/deals/${projectId}/deals/${dealId}`, {
    method: 'PATCH',
    body: JSON.stringify(data)
  }),
};
