import { apiRequest } from '@/services/api/core';

export const financeApi = {
  getOverview: async (projectId) => {
    return apiRequest(`/api/v1/finance/${projectId}/overview`);
  },

  simulate: async (projectId, config) => {
    return apiRequest(`/api/v1/finance/${projectId}/simulate`, {
      method: 'POST',
      body: JSON.stringify(config),
    });
  },

  getScenarios: async (projectId, months = 36) => {
    return apiRequest(`/api/v1/finance/${projectId}/scenarios?months=${months}`);
  },

  getValuation: async (projectId) => {
    return apiRequest(`/api/v1/finance/${projectId}/valuation`);
  },

  getMarketOpportunity: async (projectId) => {
    return apiRequest(`/api/v1/finance/${projectId}/market-opportunity`);
  },

  getUnitEconomics: async (projectId) => {
    return apiRequest(`/api/v1/finance/${projectId}/unit-economics`);
  },
};

export default financeApi;
