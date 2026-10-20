/**
 * Form controlling platform maintenance mode, user registration gates, and default quotas.
 */

import React, { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';

export default function PlatformTogglesForm({ settings, onSave }) {
  const [formData, setFormData] = useState({
    maintenance_mode: false,
    user_registration_enabled: true,
    default_free_messages: 100,
    default_free_orders: 10,
    system_announcement: '',
  });
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (settings) {
      setFormData({
        maintenance_mode: settings.maintenance_mode ?? false,
        user_registration_enabled: settings.user_registration_enabled ?? true,
        default_free_messages: settings.default_free_messages ?? 100,
        default_free_orders: settings.default_free_orders ?? 10,
        system_announcement: settings.system_announcement ?? '',
      });
    }
  }, [settings]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setSaved(false);
      await onSave({
        maintenance_mode: formData.maintenance_mode,
        user_registration_enabled: formData.user_registration_enabled,
        default_free_messages: Number(formData.default_free_messages),
        default_free_orders: Number(formData.default_free_orders),
        system_announcement: formData.system_announcement,
      });
      setSaved(true);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update settings');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="Global Platform Controls" subtitle="System availability, new signups, and default quotas">
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '600px' }}>
        {saved && (
          <div style={{ padding: '0.75rem', background: 'rgba(16, 185, 129, 0.1)', color: '#10B981', borderRadius: '6px', fontSize: '0.825rem' }}>
            Platform configuration updated successfully.
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)' }}>
            <div>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.9rem' }}>
                Maintenance Mode
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                When active, non-admin users will see a maintenance notice.
              </div>
            </div>
            <input
              type="checkbox"
              checked={formData.maintenance_mode}
              onChange={(e) => setFormData({ ...formData, maintenance_mode: e.target.checked })}
              style={{ width: '18px', height: '18px', accentColor: 'var(--danger)', cursor: 'pointer' }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)' }}>
            <div>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.9rem' }}>
                Public Merchant Registration
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Allow new store owners to sign up via public registration page.
              </div>
            </div>
            <input
              type="checkbox"
              checked={formData.user_registration_enabled}
              onChange={(e) => setFormData({ ...formData, user_registration_enabled: e.target.checked })}
              style={{ width: '18px', height: '18px', accentColor: 'var(--primary)', cursor: 'pointer' }}
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <Input
            label="Default Free Messages Quota"
            type="number"
            value={formData.default_free_messages}
            onChange={(e) => setFormData({ ...formData, default_free_messages: e.target.value })}
          />
          <Input
            label="Default Free Orders Cap"
            type="number"
            value={formData.default_free_orders}
            onChange={(e) => setFormData({ ...formData, default_free_orders: e.target.value })}
          />
        </div>

        <Input
          label="Global Banner Announcement"
          placeholder="System update scheduled at 02:00 UTC..."
          value={formData.system_announcement}
          onChange={(e) => setFormData({ ...formData, system_announcement: e.target.value })}
        />

        <div>
          <Button type="submit" variant="primary" isLoading={loading}>
            Save Platform Settings
          </Button>
        </div>
      </form>
    </Card>
  );
}
