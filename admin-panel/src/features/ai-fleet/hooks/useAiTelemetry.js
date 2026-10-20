/**
 * Hook for polling AI fleet telemetry and model performance data.
 */

import { useState, useEffect } from 'react';
import { adminApi } from '@/lib/api';

export function useAiTelemetry() {
  const [telemetry, setTelemetry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTelemetry = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await adminApi.getAiTelemetry();
      setTelemetry(res.data);
    } catch (err) {
      console.error('Failed to load AI telemetry:', err);
      setError(err.response?.data?.detail || 'Failed to fetch AI telemetry');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTelemetry();
  }, []);

  return { telemetry, loading, error, refetch: fetchTelemetry };
}
