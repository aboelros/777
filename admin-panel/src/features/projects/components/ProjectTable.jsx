/**
 * Project fleet table displaying store codes, bot profiles, and active status switches.
 */

import React from 'react';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import { Eye, Power } from 'lucide-react';

export default function ProjectTable({ projects = [], loading = false, onInspect, onToggleStatus }) {
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
        <div className="spinner" style={{ width: '32px', height: '32px' }} />
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
        No merchant stores found in the fleet.
      </div>
    );
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border)', background: 'rgba(255, 255, 255, 0.02)' }}>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Store / Brand</th>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Store Code</th>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>AI Persona</th>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Fleet Status</th>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Created</th>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {projects.map((p) => (
            <tr key={p.id} style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '1rem 1.5rem' }}>
                <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.875rem' }}>
                  {p.name}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Timezone: {p.timezone || 'UTC'}
                </div>
              </td>
              <td style={{ padding: '1rem 1.5rem' }}>
                <span style={{ fontFamily: 'monospace', fontSize: '0.8rem', background: 'rgba(255, 255, 255, 0.05)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                  {p.project_code}
                </span>
              </td>
              <td style={{ padding: '1rem 1.5rem' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {p.bot_name || 'Alex'} <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>({p.bot_tone || 'Standard'})</span>
                </div>
              </td>
              <td style={{ padding: '1rem 1.5rem' }}>
                <Badge variant={p.is_active ? 'success' : 'danger'}>
                  {p.is_active ? 'Online' : 'Disabled'}
                </Badge>
              </td>
              <td style={{ padding: '1rem 1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {p.created_at ? new Date(p.created_at).toLocaleDateString() : 'N/A'}
              </td>
              <td style={{ padding: '1rem 1.5rem', textAlign: 'right' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.5rem' }}>
                  <Button variant="ghost" size="sm" icon={Eye} onClick={() => onInspect(p)} title="Inspect Store" />
                  <Button
                    variant={p.is_active ? 'danger' : 'secondary'}
                    size="sm"
                    icon={Power}
                    onClick={() => onToggleStatus(p.id, !p.is_active)}
                    title={p.is_active ? 'Disable Store' : 'Enable Store'}
                  >
                    {p.is_active ? 'Disable' : 'Enable'}
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
