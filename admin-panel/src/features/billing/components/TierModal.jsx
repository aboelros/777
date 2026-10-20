/**
 * Modal dialog for manually overriding merchant tiers and operational usage limits.
 */

import React, { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';

export default function TierModal({ isOpen, onClose, subscription, onSave }) {
  const [tier, setTier] = useState('free');
  const [limits, setLimits] = useState({
    limit_messages: 100,
    limit_orders: 10,
    limit_ai_requests: 1000,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (subscription) {
      setTier(subscription.tier || 'free');
      setLimits({
        limit_messages: subscription.limit_messages || 100,
        limit_orders: subscription.limit_orders || 10,
        limit_ai_requests: subscription.limit_ai_requests || 1000,
      });
    }
    setError('');
  }, [subscription, isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError('');
      await onSave(subscription.user_id, {
        tier,
        limits: {
          limit_messages: Number(limits.limit_messages),
          limit_orders: Number(limits.limit_orders),
          limit_ai_requests: Number(limits.limit_ai_requests),
        },
      });
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to update subscription limits');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Override Plan & Usage Limits">
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Merchant: <strong style={{ color: 'var(--text-primary)' }}>{subscription?.user_email}</strong>
        </p>

        {error && (
          <div style={{ padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', borderRadius: '6px', fontSize: '0.825rem' }}>
            {error}
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          <label style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
            Subscription Plan Tier
          </label>
          <select
            value={tier}
            onChange={(e) => setTier(e.target.value)}
            style={{
              padding: '0.65rem 1rem',
              background: 'var(--bg-base)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text-primary)',
              fontSize: '0.875rem',
            }}
          >
            <option value="free">Free Tier</option>
            <option value="starter">Starter Plan ($29/mo)</option>
            <option value="growth">Growth Plan ($79/mo)</option>
            <option value="professional">Professional Plan ($199/mo)</option>
            <option value="scale">Scale Plan ($499/mo)</option>
            <option value="business">Business Plan ($999/mo)</option>
            <option value="enterprise">Enterprise Custom Plan</option>
          </select>
        </div>

        <Input
          label="Monthly Messages Quota"
          type="number"
          value={limits.limit_messages}
          onChange={(e) => setLimits({ ...limits, limit_messages: e.target.value })}
        />

        <Input
          label="Monthly Orders Processed Cap"
          type="number"
          value={limits.limit_orders}
          onChange={(e) => setLimits({ ...limits, limit_orders: e.target.value })}
        />

        <Input
          label="Monthly AI Requests Limit"
          type="number"
          value={limits.limit_ai_requests}
          onChange={(e) => setLimits({ ...limits, limit_ai_requests: e.target.value })}
        />

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" isLoading={loading}>
            Save Override
          </Button>
        </div>
      </form>
    </Modal>
  );
}
