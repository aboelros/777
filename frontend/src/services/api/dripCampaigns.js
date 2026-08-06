import { apiRequest, API_BASE_URL } from './core';

export const dripCampaigns = {
  getCampaigns: (projectId) => apiRequest(`/api/v1/drip-campaigns/${projectId}/campaigns`),
  createCampaign: (projectId, data) => apiRequest(`/api/v1/drip-campaigns/${projectId}/campaigns`, {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  addStep: (projectId, campaignId, data) => apiRequest(`/api/v1/drip-campaigns/${projectId}/campaigns/${campaignId}/steps`, {
    method: 'POST',
    body: JSON.stringify(data)
  }),
};
