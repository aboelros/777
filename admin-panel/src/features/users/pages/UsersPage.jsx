/**
 * Platform user management page with search, creation modal, and status mutation triggers.
 */

import React, { useState } from 'react';
import { Plus, Search } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { useUsers } from '../hooks/useUsers';
import UserTable from '../components/UserTable';
import UserModal from '../components/UserModal';
import ResetPasswordModal from '../components/ResetPasswordModal';
import UserDetailDrawer from '../components/UserDetailDrawer';

export default function UsersPage() {
  const [search, setSearch] = useState('');
  const { users, loading, error, createUser, updateUser, resetPassword, deleteUser } = useUsers(search);

  const [modalState, setModalState] = useState({ isOpen: false, user: null });
  const [resetModalState, setResetModalState] = useState({ isOpen: false, user: null });
  const [inspectState, setInspectState] = useState({ isOpen: false, user: null });

  const handleCreateOrUpdate = async (formData) => {
    if (modalState.user) {
      await updateUser(modalState.user.id, {
        name: formData.name,
        role: formData.role,
        is_active: formData.is_active,
      });
    } else {
      await createUser(formData);
    }
  };

  const handleDeactivate = async (user) => {
    if (window.confirm(`Are you sure you want to suspend account: ${user.email}?`)) {
      await deleteUser(user.id);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            User Accounts & RBAC
          </h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Manage platform merchants, role assignments, passwords, and security status
          </p>
        </div>

        <Button
          variant="primary"
          icon={Plus}
          onClick={() => setModalState({ isOpen: true, user: null })}
        >
          New Merchant
        </Button>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', borderRadius: 'var(--radius-md)' }}>
          {error}
        </div>
      )}

      {/* Main Table Card */}
      <Card noPadding>
        <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border)' }}>
          <div style={{ maxWidth: '400px' }}>
            <Input
              icon={Search}
              placeholder="Search by name or email address..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        <UserTable
          users={users}
          loading={loading}
          onInspect={(u) => setInspectState({ isOpen: true, user: u })}
          onEdit={(u) => setModalState({ isOpen: true, user: u })}
          onResetPassword={(u) => setResetModalState({ isOpen: true, user: u })}
          onDeactivate={handleDeactivate}
        />
      </Card>

      {/* Modals */}
      <UserModal
        isOpen={modalState.isOpen}
        onClose={() => setModalState({ isOpen: false, user: null })}
        onSubmit={handleCreateOrUpdate}
        initialUser={modalState.user}
      />

      <ResetPasswordModal
        isOpen={resetModalState.isOpen}
        onClose={() => setResetModalState({ isOpen: false, user: null })}
        user={resetModalState.user}
        onReset={resetPassword}
      />

      <UserDetailDrawer
        isOpen={inspectState.isOpen}
        onClose={() => setInspectState({ isOpen: false, user: null })}
        user={inspectState.user}
        onEdit={(u) => setModalState({ isOpen: true, user: u })}
        onResetPassword={(u) => setResetModalState({ isOpen: true, user: u })}
      />
    </div>
  );
}
