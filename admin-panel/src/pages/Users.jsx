import { useState, useEffect } from 'react';
import { Plus, Search, MoreVertical, Edit2, Trash2, Key, X } from 'lucide-react';
import { api } from '../lib/api';

export default function Users() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  
  // Modals
  const [showCreate, setShowCreate] = useState(false);
  const [newUser, setNewUser] = useState({ email: '', password: '', name: '', role: 'user', is_active: true });

  useEffect(() => {
    fetchUsers();
  }, [search]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/admin/users?page_size=50${search ? `&q=${search}` : ''}`);
      setUsers(res.data);
    } catch (err) {
      console.error('Failed to fetch users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      await api.post('/admin/users', newUser);
      setShowCreate(false);
      setNewUser({ email: '', password: '', name: '', role: 'user', is_active: true });
      fetchUsers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create user');
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">User Management</h1>
          <p className="text-muted mt-1">Manage accounts, roles, and access</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn btn-primary">
          <Plus size={18} />
          <span>New User</span>
        </button>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '1.25rem', borderBottom: '1px solid var(--border)', display: 'flex', gap: '1rem' }}>
          <div className="relative flex-1 max-w-md">
            <Search size={18} className="text-muted" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Search by email or name..."
              className="input-field"
              style={{ paddingLeft: '2.5rem', background: 'var(--bg-base)' }}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
          {loading ? (
            <div className="p-8 flex justify-center"><div className="spinner border-primary"></div></div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Joined</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr><td colSpan="5" className="text-center text-muted py-8">No users found.</td></tr>
                ) : (
                  users.map((user) => (
                    <tr key={user.id}>
                      <td>
                        <div className="font-medium text-primary">{user.name || 'No Name'}</div>
                        <div className="text-xs text-muted mt-1">{user.email}</div>
                      </td>
                      <td>
                        <span className={`badge ${user.role === 'admin' ? 'badge-primary' : ''}`} style={user.role === 'user' ? {background: 'rgba(255,255,255,0.1)'} : {}}>
                          {user.role}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${user.is_active ? 'badge-success' : 'badge-danger'}`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="text-muted text-sm">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td>
                        <div className="flex gap-2">
                          <button className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem' }} title="Edit User">
                            <Edit2 size={14} />
                          </button>
                          <button className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem' }} title="Reset Password">
                            <Key size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Create User Modal */}
      {showCreate && (
        <div className="modal-overlay">
          <div className="card modal-content">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">Create New User</h2>
              <button onClick={() => setShowCreate(false)} className="text-muted" style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleCreateUser} className="flex flex-col gap-4">
              <div className="input-group">
                <label className="input-label">Email</label>
                <input type="email" required className="input-field" value={newUser.email} onChange={e => setNewUser({...newUser, email: e.target.value})} />
              </div>
              
              <div className="input-group">
                <label className="input-label">Name</label>
                <input type="text" className="input-field" value={newUser.name} onChange={e => setNewUser({...newUser, name: e.target.value})} />
              </div>

              <div className="input-group">
                <label className="input-label">Password</label>
                <input type="password" required className="input-field" minLength={8} value={newUser.password} onChange={e => setNewUser({...newUser, password: e.target.value})} />
              </div>

              <div className="flex gap-4 mt-2">
                <div className="input-group">
                  <label className="input-label">Role</label>
                  <select className="input-field" value={newUser.role} onChange={e => setNewUser({...newUser, role: e.target.value})}>
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button type="button" onClick={() => setShowCreate(false)} className="btn btn-secondary">Cancel</button>
                <button type="submit" className="btn btn-primary">Create Account</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
