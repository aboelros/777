/**
 * User list table with role labels, status toggles, and contextual action menus.
 */

import React from 'react';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import { Edit2, Key, UserX, Eye } from 'lucide-react';

export default function UserTable({
  users = [],
  loading = false,
  onEdit,
  onResetPassword,
  onInspect,
  onDeactivate,
}) {
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
        <div className="spinner" style={{ width: '32px', height: '32px' }} />
      </div>
    );
  }

  if (users.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
        No merchant accounts found matching the search criteria.
      </div>
    );
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border)', background: 'rgba(255, 255, 255, 0.02)' }}>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>User</th>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Role</th>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Status</th>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Created</th>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id} style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '1rem 1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div
                    style={{
                      width: '34px',
                      height: '34px',
                      borderRadius: '8px',
                      background: u.role === 'admin' ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 600,
                      color: u.role === 'admin' ? 'var(--primary)' : 'var(--text-secondary)',
                      fontSize: '0.85rem',
                    }}
                  >
                    {(u.name || u.email || 'U')[0].toUpperCase()}
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.875rem' }}>
                      {u.name || 'Unnamed User'}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{u.email}</div>
                  </div>
                </div>
              </td>
              <td style={{ padding: '1rem 1.5rem' }}>
                <Badge variant={u.role === 'admin' ? 'primary' : 'neutral'}>
                  {u.role}
                </Badge>
              </td>
              <td style={{ padding: '1rem 1.5rem' }}>
                <Badge variant={u.is_active ? 'success' : 'danger'}>
                  {u.is_active ? 'Active' : 'Suspended'}
                </Badge>
              </td>
              <td style={{ padding: '1rem 1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A'}
              </td>
              <td style={{ padding: '1rem 1.5rem', textAlign: 'right' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.4rem' }}>
                  <Button variant="ghost" size="sm" icon={Eye} onClick={() => onInspect(u)} title="Inspect Details" />
                  <Button variant="ghost" size="sm" icon={Edit2} onClick={() => onEdit(u)} title="Edit Account" />
                  <Button variant="ghost" size="sm" icon={Key} onClick={() => onResetPassword(u)} title="Reset Password" />
                  {u.is_active && (
                    <Button variant="danger" size="sm" icon={UserX} onClick={() => onDeactivate(u)} title="Suspend User" />
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
