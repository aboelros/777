/**
 * Project fleet table displaying store codes, bot profiles, and active status switches.
 * Fully responsive with mobile horizontal touch scrolling.
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
    <div className="table-responsive-container">
      <table style={{ width: '100%', minWidth: '650px', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border)', background: 'rgba(255, 255, 255, 0.02)' }}>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Store / Brand</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Store Code</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>AI Persona</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Fleet Status</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Created</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {projects.map((p) => (
            <tr key={p.id} style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '0.9rem 1.25rem' }}>
                <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.875rem' }}>
                  {p.name}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Timezone: {p.timezone || 'UTC'}
                </div>
              </td>
              <td style={{ padding: '0.9rem 1.25rem' }}>
                <span style={{ fontFamily: 'monospace', fontSize: '0.8rem', background: 'rgba(255, 255, 255, 0.05)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                  {p.project_code}
                </span>
              </td>
              <td style={{ padding: '0.9rem 1.25rem' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {p.bot_name || 'Alex'} <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>({p.bot_tone || 'Standard'})</span>
                </div>
              </td>
              <td style={{ padding: '0.9rem 1.25rem' }}>
                <Badge variant={p.is_active ? 'success' : 'danger'}>
                  {p.is_active ? 'Active' : 'Disabled'}
                </Badge>
              </td>
              <td style={{ padding: '0.9rem 1.25rem', fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                {p.created_at ? new Date(p.created_at).toLocaleDateString() : 'N/A'}
              </td>
              <td style={{ padding: '0.9rem 1.25rem', textAlign: 'right' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.4rem' }}>
                  <Button variant="ghost" size="sm" onClick={() => onInspect?.(p)} title="Inspect Store">
                    <Eye size={15} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onToggleStatus?.(p)}
                    title={p.is_active ? 'Disable' : 'Enable'}
                    style={{ color: p.is_active ? 'var(--danger)' : 'var(--success)' }}
                  >
                    <Power size={15} />
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
