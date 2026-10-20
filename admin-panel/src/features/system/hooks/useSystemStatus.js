/**
 * Hook for polling system diagnostics, latency, and audit logs.
 */

import { useState, useEffect } from 'react';
import { adminApi } from '@/lib/api';

export function useSystemStatus() {
  const [health, setHealth] = useState(null);
  const [auditLogs, setAuditLogs] = useState({ total: 0, items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const [hRes, aRes] = await Promise.all([
        adminApi.getHealth(),
        adminApi.getAuditLogs(),
      ]);
      setHealth(hRes.data);
      setAuditLogs(aRes.data);
    } catch (err) {
      console.error('Failed to poll system status:', err);
      setError(err.response?.data?.detail || 'Failed to poll system diagnostics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return { health, auditLogs: auditLogs.items, loading, error, refetch: fetchStatus };
}
