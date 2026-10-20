/**
 * Master layout shell for the administrative command center.
 */

import React, { useEffect } from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import ErrorBoundary from '@/components/ui/ErrorBoundary';
import { useAdminStore } from '@/store/adminStore';

export default function Layout() {
  const { isAuthenticated } = useAdminStore();

  if (!isAuthenticated && !localStorage.getItem('admin_token')) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-base)' }}>
      <Sidebar />
      <div
        style={{
          marginLeft: 'var(--sidebar-width)',
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          minWidth: 0,
        }}
      >
        <Header />
        <main style={{ padding: '2rem', flex: 1 }}>
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
