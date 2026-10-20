/**
 * Form for global AI model candidates, temperature, and fallback policies.
 */

import React, { useState } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { adminApi } from '@/lib/api';

export default function ModelConfigForm({ telemetry, onUpdated }) {
  const [model, setModel] = useState(telemetry?.primary_model || 'gemini-2.5-flash');
  const [temperature, setTemperature] = useState(telemetry?.temperature || 0.7);
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setSaved(false);
      await adminApi.updateSettings({
        ai_primary_model: model,
        ai_temperature: Number(temperature),
      });
      setSaved(true);
      if (onUpdated) onUpdated();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update AI settings');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="Global AI Engine Configuration" subtitle="Configure platform-wide inference model and temperature">
      <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', maxWidth: '600px' }}>
        {saved && (
          <div style={{ padding: '0.75rem', background: 'rgba(16, 185, 129, 0.1)', color: '#10B981', borderRadius: '6px', fontSize: '0.825rem' }}>
            AI engine parameters updated successfully across all tenant bots.
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          <label style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
            Primary Inference Model
          </label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            style={{
              padding: '0.65rem 1rem',
              background: 'var(--bg-base)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text-primary)',
              fontSize: '0.875rem',
            }}
          >
            <option value="gemini-2.5-flash">Gemini 2.5 Flash (Ultra-low latency, High Reasoning)</option>
            <option value="gemini-2.0-flash">Gemini 2.0 Flash (Stable Fallback)</option>
            <option value="gemini-1.5-pro">Gemini 1.5 Pro (Deep Contextual Analysis)</option>
          </select>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          <label style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
            Model Temperature ({temperature})
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={temperature}
            onChange={(e) => setTemperature(parseFloat(e.target.value))}
            style={{ accentColor: 'var(--primary)', cursor: 'pointer' }}
          />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Lower values produce consistent, factual answers; higher values produce more creative bot conversations.
          </span>
        </div>

        <div>
          <Button type="submit" variant="primary" isLoading={loading}>
            Save AI Parameters
          </Button>
        </div>
      </form>
    </Card>
  );
}
