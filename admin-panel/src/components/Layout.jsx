/**
 * Master responsive layout shell for the administrative command center.
 * Controls mobile sidebar drawer state and responsive padding.
 */

import React from 'react';
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
        className="admin-layout-content"
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          minWidth: 0,
          transition: 'margin-left 0.25s ease',
        }}
      >
        <Header />
        <main className="admin-layout-main" style={{ flex: 1, minWidth: 0 }}>
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
