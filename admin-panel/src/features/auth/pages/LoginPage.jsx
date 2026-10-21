/**
 * Administrative login portal with credentials verification and admin role guard.
 * Features Automio Neuro-Prism branding and mobile-optimized touch form controls.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Mail, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';
import { useAdminStore } from '@/store/adminStore';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Logo from '@/components/brand/Logo';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setUser } = useAdminStore();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await api.post('/auth/login', {
        email: email.trim(),
        password,
      });

      const { access_token } = response.data;
      if (!access_token) {
        throw new Error('No access token returned by authentication service.');
      }

      localStorage.setItem('admin_token', access_token);

      let user = null;
      try {
        const meRes = await api.get('/auth/me', {
          headers: { Authorization: `Bearer ${access_token}` },
        });
        user = meRes.data;
      } catch {
        // Fallback to token payload
        const base64Url = access_token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const payload = JSON.parse(window.atob(base64));
        user = { id: payload.sub, email: payload.email, role: payload.role };
      }

      if (user?.role !== 'admin') {
        localStorage.removeItem('admin_token');
        setError('Unauthorized: Root administrator privileges are required to access this portal.');
        setLoading(false);
        return;
      }

      setUser(user, access_token);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Invalid administrator email or password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: 'radial-gradient(circle at 50% 15%, rgba(14, 165, 233, 0.12) 0%, #020617 75%)',
        padding: '1.25rem',
        boxSizing: 'border-box',
      }}
    >
      <div
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: '420px',
          padding: '2.25rem 1.75rem',
          borderRadius: 'var(--radius-lg)',
          boxShadow: '0 24px 64px rgba(0, 0, 0, 0.6)',
          border: '1px solid var(--border)',
          animation: 'fadeIn 0.3s ease-out',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '2rem' }}>
          <Logo size={42} variant="full" subtitle="ADMIN COMMANDER" />
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.85rem', textAlign: 'center' }}>
            Root infrastructure & operational console
          </p>
        </div>

        {error && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              padding: '0.75rem 1rem',
              marginBottom: '1.5rem',
              background: 'rgba(244, 63, 94, 0.12)',
              border: '1px solid rgba(244, 63, 94, 0.35)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--danger)',
              fontSize: '0.825rem',
              lineHeight: 1.4,
            }}
          >
            <AlertCircle size={18} style={{ flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <Input
            label="Administrator Email"
            type="email"
            required
            icon={Mail}
            placeholder="admin@platform.local"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <Input
            label="Root Password"
            type="password"
            required
            icon={Lock}
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={loading}
            style={{ marginTop: '0.5rem', width: '100%' }}
          >
            Enter Command Center
          </Button>
        </form>
      </div>
    </div>
  );
}
