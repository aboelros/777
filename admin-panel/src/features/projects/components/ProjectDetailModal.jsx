/**
 * Inspection modal for tenant project metadata and AI instructions.
 */

import React from 'react';
import Modal from '@/components/ui/Modal';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';

export default function ProjectDetailModal({ isOpen, onClose, project }) {
  if (!project) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Store Fleet Inspector" maxWidth="600px">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div>
          <h4 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            {project.name}
          </h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Project Code: <strong style={{ color: 'var(--text-secondary)' }}>{project.project_code}</strong>
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Store ID</span>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontFamily: 'monospace', wordBreak: 'break-all' }}>
              {project.id}
            </p>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Fleet Status</span>
            <div style={{ marginTop: '0.2rem' }}>
              <Badge variant={project.is_active ? 'success' : 'danger'}>
                {project.is_active ? 'Active' : 'Disabled'}
              </Badge>
            </div>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>AI Assistant Name</span>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{project.bot_name || 'Alex'}</p>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Bot Personality Tone</span>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{project.bot_tone || 'Professional'}</p>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '1.25rem', borderTop: '1px solid var(--border)' }}>
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
}
