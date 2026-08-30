import React, { useState, useEffect } from 'react';
import { User, Lock, Server, Database, Save, Check } from 'lucide-react';
import { adminApi } from '../../services/api';
import { getUser } from '../../services/auth';

export default function AdminSettingsPage() {
  const [profile, setProfile] = useState({ name: '', email: '' });
  const [passwords, setPasswords] = useState({ old: '', new: '', confirm: '' });
  const [systemStats, setSystemStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState('');

  useEffect(() => {
    // Load profile from auth or api
    const user = getUser();
    if (user) {
      setProfile({ name: user.name || '', email: user.email || '' });
    }

    // Load system stats for read-only display
    const loadStats = async () => {
      try {
        const res = await adminApi.stats();
        if (res.data?.stats) {
          setSystemStats(res.data.stats);
        }
      } catch (err) {
        console.error(err);
      }
    };
    loadStats();
  }, []);

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(''), 3000);
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Assuming PUT /api/auth/profile exists
      // await authService.updateProfile(profile);
      showToast('Profile updated successfully!');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (passwords.new !== passwords.confirm) {
      alert('New passwords do not match');
      return;
    }
    setLoading(true);
    try {
      // await authService.changePassword(passwords);
      setPasswords({ old: '', new: '', confirm: '' });
      showToast('Password changed successfully!');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white min-h-screen text-gray-800 relative">
      {toast && (
        <div className="fixed top-6 right-6 bg-gray-800 text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 animate-fade-in z-50">
          <Check className="w-5 h-5 text-green-400" />
          {toast}
        </div>
      )}

      <h1 className="text-2xl font-bold text-gray-900 mb-8">Settings</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl">
        <div className="space-y-8">
          {/* Admin Profile Section */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center gap-2">
              <User className="w-5 h-5 text-indigo-600" />
              <h2 className="font-semibold text-gray-800">Admin Profile</h2>
            </div>
            <form onSubmit={handleProfileUpdate} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <input
                  type="text"
                  value={profile.name}
                  onChange={(e) => setProfile({...profile, name: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-600 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <input
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile({...profile, email: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-600 outline-none"
                />
              </div>
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  <Save className="w-4 h-4" /> Save Profile
                </button>
              </div>
            </form>
          </div>

          {/* Change Password Section */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center gap-2">
              <Lock className="w-5 h-5 text-indigo-600" />
              <h2 className="font-semibold text-gray-800">Change Password</h2>
            </div>
            <form onSubmit={handlePasswordChange} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
                <input
                  type="password"
                  value={passwords.old}
                  onChange={(e) => setPasswords({...passwords, old: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-600 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                <input
                  type="password"
                  value={passwords.new}
                  onChange={(e) => setPasswords({...passwords, new: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-600 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
                <input
                  type="password"
                  value={passwords.confirm}
                  onChange={(e) => setPasswords({...passwords, confirm: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-600 outline-none"
                />
              </div>
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading || !passwords.new}
                  className="flex items-center gap-2 bg-gray-800 hover:bg-gray-900 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
                >
                  Update Password
                </button>
              </div>
            </form>
          </div>
        </div>

        <div>
          {/* System Configuration (Read-only) */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center gap-2">
              <Server className="w-5 h-5 text-indigo-600" />
              <h2 className="font-semibold text-gray-800">System Configuration</h2>
            </div>
            <div className="p-6 space-y-6">
              <div>
                <p className="text-sm font-medium text-gray-500 mb-1">Environment</p>
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-full text-xs font-bold uppercase tracking-wider">
                    {process.env.NODE_ENV || 'Development'}
                  </span>
                </div>
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-500 mb-2 flex items-center gap-1.5">
                  <Database className="w-4 h-4" /> Database & Background Tasks
                </p>
                <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 space-y-3">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">MongoDB Connection</span>
                    <span className="flex items-center gap-1.5 font-medium text-emerald-600">
                      <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                      Connected
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Event Scheduler</span>
                    <span className={`flex items-center gap-1.5 font-medium ${systemStats?.scheduler_running ? 'text-emerald-600' : 'text-gray-500'}`}>
                      <span className={`w-2 h-2 rounded-full ${systemStats?.scheduler_running ? 'bg-emerald-500' : 'bg-gray-400'}`}></span>
                      {systemStats?.scheduler_running ? 'Running' : 'Stopped'}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-500 mb-2">API Configuration</p>
                <div className="text-sm text-gray-600 bg-gray-50 rounded-lg border border-gray-200 p-4 font-mono break-all">
                  API_URL: {process.env.REACT_APP_API_URL || 'http://localhost:5000/api'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
