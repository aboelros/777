/**
 * Store fleet management page displaying all merchant projects, codes, and operational toggles.
 */

import React, { useState } from 'react';
import { Search } from 'lucide-react';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import { useProjects } from '../hooks/useProjects';
import ProjectTable from '../components/ProjectTable';
import ProjectDetailModal from '../components/ProjectDetailModal';

export default function ProjectsPage() {
  const [search, setSearch] = useState('');
  const { projects, loading, error, toggleProjectStatus } = useProjects(search);
  const [inspectModal, setInspectModal] = useState({ isOpen: false, project: null });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>
          Merchant Store Fleet
        </h1>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
          Oversight and lifecycle controls for all multi-tenant projects, brands, and automated bots
        </p>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', borderRadius: 'var(--radius-md)' }}>
          {error}
        </div>
      )}

      <Card noPadding>
        <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border)' }}>
          <div style={{ maxWidth: '400px' }}>
            <Input
              icon={Search}
              placeholder="Search by store name or project code..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        <ProjectTable
          projects={projects}
          loading={loading}
          onInspect={(p) => setInspectModal({ isOpen: true, project: p })}
          onToggleStatus={toggleProjectStatus}
        />
      </Card>

      <ProjectDetailModal
        isOpen={inspectModal.isOpen}
        onClose={() => setInspectModal({ isOpen: false, project: null })}
        project={inspectModal.project}
      />
    </div>
  );
}
