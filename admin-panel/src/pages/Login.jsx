import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Mail, AlertCircle, ShieldCheck } from 'lucide-react';
import { api } from '../lib/api';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', email); // OAuth2 expects 'username' for email
      formData.append('password', password);

      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      const data = response.data;
      
      // Check if user is actually admin
      if (data.user.role !== 'admin') {
        setError('Unauthorized: Admin access required.');
        setLoading(false);
        return;
      }

      localStorage.setItem('admin_token', data.access_token);
      localStorage.setItem('admin_user', JSON.stringify(data.user));
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen relative" style={{ backgroundImage: 'radial-gradient(circle at 50% -20%, #1a1a2e 0%, var(--bg-base) 60%)' }}>
      
      {/* Background decoration */}
      <div style={{ position: 'absolute', top: '10%', left: '15%', width: '300px', height: '300px', background: 'var(--primary)', filter: 'blur(150px)', opacity: 0.15, borderRadius: '50%' }} />
      <div style={{ position: 'absolute', bottom: '10%', right: '15%', width: '300px', height: '300px', background: 'var(--success)', filter: 'blur(150px)', opacity: 0.1, borderRadius: '50%' }} />

      <div className="glass-panel p-8 w-full max-w-md relative z-10 animate-fade-in" style={{ padding: '2.5rem' }}>
        <div className="flex flex-col items-center mb-8">
          <div className="flex items-center justify-center mb-4" style={{ width: '60px', height: '60px', borderRadius: '16px', background: 'var(--primary-light)' }}>
            <ShieldCheck size={32} color="var(--primary)" />
          </div>
          <h1 className="text-2xl font-bold">Admin Portal</h1>
          <p className="text-muted text-sm mt-2">Sign in to manage the platform</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 mb-6" style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', borderRadius: 'var(--radius-md)', fontSize: '0.875rem' }}>
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="flex flex-col gap-5">
          <div className="input-group">
            <label className="input-label">Email Address</label>
            <div className="relative flex items-center">
              <Mail size={18} className="text-muted" style={{ position: 'absolute', left: '1rem' }} />
              <input
                type="email"
                required
                className="input-field"
                style={{ paddingLeft: '2.5rem' }}
                placeholder="admin@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <div className="input-group">
            <label className="input-label">Password</label>
            <div className="relative flex items-center">
              <Lock size={18} className="text-muted" style={{ position: 'absolute', left: '1rem' }} />
              <input
                type="password"
                required
                className="input-field"
                style={{ paddingLeft: '2.5rem' }}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary mt-4" 
            style={{ padding: '0.875rem', fontSize: '1rem' }}
            disabled={loading}
          >
            {loading ? <div className="spinner"></div> : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}
