/**
 * User list table with role labels, status toggles, and contextual action menus.
 * Fully responsive with mobile horizontal touch scrolling.
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
    <div className="table-responsive-container">
      <table style={{ width: '100%', minWidth: '650px', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border)', background: 'rgba(255, 255, 255, 0.02)' }}>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>User</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Role</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Status</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Created</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id} style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '0.9rem 1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div
                    style={{
                      width: '34px',
                      height: '34px',
                      borderRadius: '8px',
                      background: u.role === 'admin' ? 'var(--primary-light)' : 'rgba(255, 255, 255, 0.05)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 600,
                      color: u.role === 'admin' ? 'var(--primary)' : 'var(--text-secondary)',
                      fontSize: '0.85rem',
                      flexShrink: 0,
                    }}
                  >
                    {(u.name || u.email || 'U').charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                      {u.name || 'Unnamed Merchant'}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {u.email}
                    </div>
                  </div>
                </div>
              </td>
              <td style={{ padding: '0.9rem 1.25rem' }}>
                <Badge variant={u.role === 'admin' ? 'primary' : 'outline'}>
                  {u.role ? u.role.toUpperCase() : 'USER'}
                </Badge>
              </td>
              <td style={{ padding: '0.9rem 1.25rem' }}>
                <Badge variant={u.is_active ? 'success' : 'danger'}>
                  {u.is_active ? 'Active' : 'Suspended'}
                </Badge>
              </td>
              <td style={{ padding: '0.9rem 1.25rem', fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                {u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A'}
              </td>
              <td style={{ padding: '0.9rem 1.25rem', textAlign: 'right' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.4rem' }}>
                  <Button variant="ghost" size="sm" onClick={() => onInspect?.(u)} title="Inspect">
                    <Eye size={15} />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => onEdit?.(u)} title="Edit Role">
                    <Edit2 size={15} />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => onResetPassword?.(u)} title="Reset Password">
                    <Key size={15} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDeactivate?.(u)}
                    title={u.is_active ? 'Suspend' : 'Activate'}
                    style={{ color: u.is_active ? 'var(--danger)' : 'var(--success)' }}
                  >
                    <UserX size={15} />
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
