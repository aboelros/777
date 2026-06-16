import { useState, useEffect } from 'react';
import { Activity, MessageSquare, ShoppingCart, Users, TrendingUp } from 'lucide-react';
import { api } from '../lib/api';

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/admin/usage/summary?days=30');
        setStats(response.data);
      } catch (err) {
        setError(err.message || 'Failed to load dashboard metrics');
      } finally {
        setLoading(false);
      }
    };
    
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <div className="spinner" style={{ width: '40px', height: '40px', borderWidth: '3px' }}></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 rounded-lg bg-red-900/20 text-red-400 border border-red-500/20">
        <h3 className="font-semibold mb-1">Error Loading Dashboard</h3>
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Messages',
      value: stats?.total_messages || 0,
      icon: MessageSquare,
      color: 'var(--primary)',
      bg: 'var(--primary-light)'
    },
    {
      title: 'Inbound Messages',
      value: stats?.inbound_messages || 0,
      icon: Users,
      color: 'var(--warning)',
      bg: 'rgba(245, 158, 11, 0.15)'
    },
    {
      title: 'AI Responses',
      value: stats?.outbound_messages || 0,
      icon: Activity,
      color: 'var(--success)',
      bg: 'rgba(16, 185, 129, 0.15)'
    },
    {
      title: 'Orders Processed',
      value: stats?.total_orders || 0,
      icon: ShoppingCart,
      color: '#EC4899',
      bg: 'rgba(236, 72, 153, 0.15)'
    }
  ];

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Platform Overview</h1>
          <p className="text-muted mt-1">System activity and usage over the last 30 days</p>
        </div>
        
        <div className="badge badge-success flex items-center gap-1" style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>
          <TrendingUp size={16} />
          <span>System Healthy</span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        {statCards.map((card, idx) => (
          <div key={idx} className="card flex items-center justify-between">
            <div>
              <p className="text-muted text-sm font-medium mb-1">{card.title}</p>
              <h3 className="text-2xl font-bold">{card.value.toLocaleString()}</h3>
            </div>
            <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: card.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <card.icon size={24} color={card.color} />
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <h3 className="font-semibold text-lg mb-4">Quick Actions</h3>
        <div className="flex gap-4">
          <a href="/users" className="btn btn-primary">Manage Users</a>
          <button className="btn btn-secondary">View System Logs</button>
        </div>
      </div>
    </div>
  );
}
