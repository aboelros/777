/**
 * Hook for administrative user CRUD operations and status mutations.
 */

import { useState, useEffect } from 'react';
import { adminApi } from '@/lib/api';

export function useUsers(searchQuery = '', page = 1) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await adminApi.getUsers(searchQuery, page);
      setUsers(res.data);
    } catch (err) {
      console.error('Failed to fetch users:', err);
      setError(err.response?.data?.detail || 'Failed to load user list');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [searchQuery, page]);

  const createUser = async (payload) => {
    const res = await adminApi.createUser(payload);
    await fetchUsers();
    return res.data;
  };

  const updateUser = async (userId, payload) => {
    const res = await adminApi.updateUser(userId, payload);
    await fetchUsers();
    return res.data;
  };

  const resetPassword = async (userId, newPassword) => {
    await adminApi.resetPassword(userId, newPassword);
  };

  const deleteUser = async (userId) => {
    await adminApi.deleteUser(userId);
    await fetchUsers();
  };

  return {
    users,
    loading,
    error,
    refetch: fetchUsers,
    createUser,
    updateUser,
    resetPassword,
    deleteUser,
  };
}
