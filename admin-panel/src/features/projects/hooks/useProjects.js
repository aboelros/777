/**
 * Hook for managing and querying the multi-tenant store project fleet.
 */

import { useState, useEffect } from 'react';
import { adminApi } from '@/lib/api';

export function useProjects(searchQuery = '', page = 1) {
  const [data, setData] = useState({ total: 0, items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await adminApi.getProjects(searchQuery, page);
      setData(res.data);
    } catch (err) {
      console.error('Failed to fetch projects fleet:', err);
      setError(err.response?.data?.detail || 'Failed to load project fleet');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [searchQuery, page]);

  const toggleProjectStatus = async (projectId, isActive) => {
    await adminApi.updateProject(projectId, { is_active: isActive });
    await fetchProjects();
  };

  return {
    projects: data.items,
    total: data.total,
    loading,
    error,
    refetch: fetchProjects,
    toggleProjectStatus,
  };
}
