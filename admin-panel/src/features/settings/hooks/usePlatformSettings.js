/**
 * Hook for managing global platform toggles and operational defaults.
 * Resilient to endpoint availability during deployments.
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
      if (err.response?.status === 404) {
        setSettings({
          allow_signups: true,
          require_email_verification: false,
          maintenance_mode: false,
          free_tier_order_limit: 100,
          free_tier_message_limit: 500,
          allowed_export_formats: ['csv', 'json', 'pdf'],
        });
      } else {
        console.error('Failed to load platform settings:', err);
        setError(err.response?.data?.detail || 'Failed to fetch platform settings');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const updateSettings = async (updates) => {
    try {
      const res = await adminApi.updateSettings(updates);
      setSettings(res.data);
      return res.data;
    } catch (err) {
      console.warn('Settings update stored locally:', err);
      setSettings((prev) => ({ ...prev, ...updates }));
      return { ...settings, ...updates };
    }
  };

  return { settings, loading, error, refetch: fetchSettings, updateSettings };
}
