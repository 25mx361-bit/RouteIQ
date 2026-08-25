import React, { useState, useEffect } from 'react';
import { ArrowLeft, Users, UserX, Shield, RefreshCw } from 'lucide-react';
import { adminApi } from '../../services/api';

export default function UsersPage({ onBack }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const res = await adminApi.users({ limit: 100 });
      setUsers(res.data.users);
    } catch (err) {
      setError(err.message || 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await adminApi.updateRole(userId, newRole);
      fetchUsers();
    } catch (err) {
      alert(err.message || 'Failed to update role');
    }
  };

  const handleDeactivate = async (userId) => {
    if (!window.confirm('Are you sure you want to deactivate this user?')) return;
    try {
      await adminApi.deactivateUser(userId);
      fetchUsers();
    } catch (err) {
      alert(err.message || 'Failed to deactivate user');
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-950 text-slate-100 overflow-y-auto">
      <header className="shrink-0 h-16 bg-slate-900/80 backdrop-blur border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-4">
          <button onClick={onBack} className="p-2 -ml-2 rounded-lg hover:bg-slate-800 text-slate-400">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-lg font-bold flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-400" />
              User Management
            </h1>
          </div>
        </div>
        <button onClick={fetchUsers} className="p-2 rounded-lg hover:bg-slate-800 text-slate-400">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </header>

      <div className="max-w-6xl w-full mx-auto p-6 space-y-6">
        {error && <div className="text-rose-400 text-sm p-4 bg-rose-500/10 rounded-xl">{error}</div>}

        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/50 border-b border-slate-700 text-slate-400">
              <tr>
                <th className="px-4 py-3 font-semibold">Name</th>
                <th className="px-4 py-3 font-semibold">Email</th>
                <th className="px-4 py-3 font-semibold">Role</th>
                <th className="px-4 py-3 font-semibold">Status</th>
                <th className="px-4 py-3 font-semibold">Joined</th>
                <th className="px-4 py-3 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {users.map(user => (
                <tr key={user._id} className="hover:bg-slate-800/20">
                  <td className="px-4 py-3 font-medium">{user.name}</td>
                  <td className="px-4 py-3 text-slate-300">{user.email}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                      user.role === 'admin' ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30' : 'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                      user.is_active !== false ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                    }`}>
                      {user.is_active !== false ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-400">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-right space-x-2">
                    {user.role === 'user' ? (
                      <button
                        onClick={() => handleRoleChange(user._id, 'admin')}
                        className="p-1.5 rounded bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 transition-colors"
                        title="Make Admin"
                      >
                        <Shield className="w-4 h-4" />
                      </button>
                    ) : (
                      <button
                        onClick={() => handleRoleChange(user._id, 'user')}
                        className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 transition-colors"
                        title="Remove Admin"
                      >
                        <Users className="w-4 h-4" />
                      </button>
                    )}
                    {user.is_active !== false && (
                      <button
                        onClick={() => handleDeactivate(user._id)}
                        className="p-1.5 rounded bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 transition-colors"
                        title="Deactivate User"
                      >
                        <UserX className="w-4 h-4" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {users.length === 0 && !loading && (
                <tr>
                  <td colSpan="6" className="text-center py-8 text-slate-500">No users found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
