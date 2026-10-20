/**
 * Hook for managing global platform toggles and operational defaults.
 */

import { useState, useEffect } from 'react';
import { adminApi } from '@/lib/api';

export function usePlatformSettings() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await adminApi.getSettings();
      setSettings(res.data);
    } catch (err) {
      console.error('Failed to load platform settings:', err);
      setError(err.response?.data?.detail || 'Failed to fetch platform settings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const updateSettings = async (updates) => {
    const res = await adminApi.updateSettings(updates);
    setSettings(res.data);
    return res.data;
  };

  return { settings, loading, error, refetch: fetchSettings, updateSettings };
}
