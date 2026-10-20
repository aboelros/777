/**
 * Main application router configuring all feature modules, lazy loading, and error boundaries.
 */

import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ui/ErrorBoundary';

const LoginPage = lazy(() => import('@/features/auth/pages/LoginPage'));
const DashboardPage = lazy(() => import('@/features/dashboard/pages/DashboardPage'));
const UsersPage = lazy(() => import('@/features/users/pages/UsersPage'));
const ProjectsPage = lazy(() => import('@/features/projects/pages/ProjectsPage'));
const BillingPage = lazy(() => import('@/features/billing/pages/BillingPage'));
const AiFleetPage = lazy(() => import('@/features/ai-fleet/pages/AiFleetPage'));
const WebhooksPage = lazy(() => import('@/features/webhooks/pages/WebhooksPage'));
const SystemHealthPage = lazy(() => import('@/features/system/pages/SystemHealthPage'));
const SettingsPage = lazy(() => import('@/features/settings/pages/SettingsPage'));

function PageLoader() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
      <div className="spinner" style={{ width: '40px', height: '40px' }} />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<Layout />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/users" element={<UsersPage />} />
              <Route path="/projects" element={<ProjectsPage />} />
              <Route path="/billing" element={<BillingPage />} />
              <Route path="/ai-fleet" element={<AiFleetPage />} />
              <Route path="/webhooks" element={<WebhooksPage />} />
              <Route path="/system" element={<SystemHealthPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </BrowserRouter>
  );
}
