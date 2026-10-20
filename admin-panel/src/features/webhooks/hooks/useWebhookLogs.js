/**
 * Hook for polling webhook event deliveries and dispatching retry requests.
 */

import { useState, useEffect } from 'react';
import { adminApi } from '@/lib/api';

export function useWebhookLogs(page = 1, statusFilter = '') {
  const [data, setData] = useState({ total: 0, items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await adminApi.getWebhookLogs(page, statusFilter);
      setData(res.data);
    } catch (err) {
      console.error('Failed to load webhook logs:', err);
      setError(err.response?.data?.detail || 'Failed to fetch webhook records');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, statusFilter]);

  const retryWebhook = async (deliveryId) => {
    await adminApi.retryWebhook(deliveryId);
    await fetchLogs();
  };

  return {
    logs: data.items,
    total: data.total,
    loading,
    error,
    refetch: fetchLogs,
    retryWebhook,
  };
}
