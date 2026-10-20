/**
 * Modal dialog for securely resetting an account password.
 */

import React, { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';

export default function ResetPasswordModal({ isOpen, onClose, user, onReset }) {
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }
    try {
      setLoading(true);
      setError('');
      await onReset(user.id, password);
      setPassword('');
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Reset Account Password">
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Resetting password for: <strong style={{ color: 'var(--text-primary)' }}>{user?.email}</strong>
        </p>

        {error && (
          <div style={{ padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', borderRadius: '6px', fontSize: '0.825rem' }}>
            {error}
          </div>
        )}

        <Input
          label="New Strong Password"
          type="password"
          required
          placeholder="Minimum 8 characters"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="danger" isLoading={loading}>
            Confirm Reset
          </Button>
        </div>
      </form>
    </Modal>
  );
}
