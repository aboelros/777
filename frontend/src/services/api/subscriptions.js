import { apiRequest, API_BASE_URL } from './core';

export const subscriptions = {
  getPlans: async () => {
    return apiRequest('/api/v1/subscriptions/plans');
  },

  getMySubscription: async () => {
    return apiRequest('/api/v1/subscriptions/my-subscription');
  },

  getUsagePercentage: async () => {
    return apiRequest('/api/v1/subscriptions/usage-percentage');
  },

  getUsageAlerts: async () => {
    return apiRequest('/api/v1/subscriptions/usage-alerts');
  },

  getOverages: async () => {
    return apiRequest('/api/v1/subscriptions/overages');
  },

  upgrade: async (data) => {
    return apiRequest('/api/v1/subscriptions/upgrade', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  cancel: async () => {
    return apiRequest('/api/v1/subscriptions/cancel', {
      method: 'POST',
    });
  },
};
