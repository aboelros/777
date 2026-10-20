/**
 * Inspection modal drawer displaying full account metadata and security state.
 */

import React from 'react';
import Modal from '@/components/ui/Modal';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';

export default function UserDetailDrawer({ isOpen, onClose, user, onEdit, onResetPassword }) {
  if (!user) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Account Inspector" maxWidth="600px">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', paddingBottom: '1.25rem', borderBottom: '1px solid var(--border)' }}>
          <div
            style={{
              width: '54px',
              height: '54px',
              borderRadius: '12px',
              background: 'var(--primary-light)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.5rem',
              fontWeight: 700,
              color: 'var(--primary)',
            }}
          >
            {(user.name || user.email || 'U')[0].toUpperCase()}
          </div>
          <div>
            <h4 style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              {user.name || 'Merchant Account'}
            </h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{user.email}</p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>User ID</span>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontFamily: 'monospace', wordBreak: 'break-all' }}>
              {user.id}
            </p>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>System Role</span>
            <div style={{ marginTop: '0.2rem' }}>
              <Badge variant={user.role === 'admin' ? 'primary' : 'neutral'}>{user.role}</Badge>
            </div>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Account Status</span>
            <div style={{ marginTop: '0.2rem' }}>
              <Badge variant={user.is_active ? 'success' : 'danger'}>
                {user.is_active ? 'Active' : 'Suspended'}
              </Badge>
            </div>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Registration Date</span>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              {user.created_at ? new Date(user.created_at).toLocaleString() : 'N/A'}
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', paddingTop: '1.25rem', borderTop: '1px solid var(--border)' }}>
          <Button variant="secondary" onClick={() => { onClose(); onResetPassword(user); }}>
            Reset Password
          </Button>
          <Button variant="primary" onClick={() => { onClose(); onEdit(user); }}>
            Edit Account
          </Button>
        </div>
      </div>
    </Modal>
  );
}
