/**
 * Hook to fetch overview metrics and system diagnostics.
 */

import { useState, useEffect } from 'react';
import { adminApi } from '@/lib/api';

export function useDashboardMetrics(days = 30) {
  const [metrics, setMetrics] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [metricsRes, healthRes] = await Promise.all([
        adminApi.getDashboard(days),
        adminApi.getHealth(),
      ]);
      setMetrics(metricsRes.data);
      setHealth(healthRes.data);
    } catch (err) {
      console.error('Failed to load dashboard metrics:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to load telemetry');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [days]);

  return { metrics, health, loading, error, refetch: fetchData };
}
