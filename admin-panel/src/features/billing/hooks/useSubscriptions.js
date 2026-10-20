/**
 * Hook for managing SaaS subscriptions, billing tiers, and quota limits.
 */

import { useState, useEffect } from 'react';
import { adminApi } from '@/lib/api';

export function useSubscriptions(page = 1) {
  const [data, setData] = useState({ total: 0, items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSubscriptions = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await adminApi.getSubscriptions(page);
      setData(res.data);
    } catch (err) {
      console.error('Failed to load subscriptions:', err);
      setError(err.response?.data?.detail || 'Failed to fetch subscription records');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscriptions();
  }, [page]);

  const overrideLimits = async (userId, payload) => {
    await adminApi.overrideSubscription(userId, payload);
    await fetchSubscriptions();
  };

  return {
    subscriptions: data.items,
    total: data.total,
    loading,
    error,
    refetch: fetchSubscriptions,
    overrideLimits,
  };
}
