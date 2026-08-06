import { apiRequest, API_BASE_URL } from './core';

export const payments = {
  createLink: (projectId, data) => apiRequest(`/api/v1/payments/${projectId}/payment-links`, {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  getInvoices: (projectId) => apiRequest(`/api/v1/payments/${projectId}/invoices`),
  createInvoice: (projectId, data) => apiRequest(`/api/v1/payments/${projectId}/invoices`, {
    method: 'POST',
    body: JSON.stringify(data)
  }),
};
