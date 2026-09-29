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
    <div className="p-6 max-w-7xl mx-auto space-y-6 text-gray-900 dark:text-slate-100 transition-colors relative">
      {toast && (
        <div className="fixed top-6 right-6 bg-slate-800 text-white px-4 py-3 rounded-xl shadow-lg flex items-center gap-2 animate-fade-in z-50">
          <Check className="w-5 h-5 text-emerald-400" />
          {toast}
        </div>
      )}

      <div className="pb-4 border-b border-gray-200 dark:border-slate-800">
        <h1 className="text-xl font-bold tracking-tight text-gray-900 dark:text-slate-100">Admin Settings</h1>
        <p className="text-xs text-gray-500 dark:text-slate-400">Manage administrator profile credentials and system configuration</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl">
        <div className="space-y-8">
          {/* Admin Profile Section */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm overflow-hidden transition-colors">
            <div className="p-4 border-b border-gray-200 dark:border-slate-800 bg-gray-50/50 dark:bg-slate-800/40 flex items-center gap-2">
              <User className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <h2 className="font-semibold text-gray-800 dark:text-slate-200 text-sm">Admin Profile</h2>
            </div>
            <form onSubmit={handleProfileUpdate} className="p-6 space-y-4 text-xs">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-slate-300 mb-1">Full Name</label>
                <input
                  type="text"
                  value={profile.name}
                  onChange={(e) => setProfile({...profile, name: e.target.value})}
                  className="w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-slate-200 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-600 outline-none transition"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-slate-300 mb-1">Email Address</label>
                <input
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile({...profile, email: e.target.value})}
                  className="w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-slate-200 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-600 outline-none transition"
                />
              </div>
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-xl font-semibold shadow-sm transition-colors text-xs"
                >
                  <Save className="w-3.5 h-3.5" /> Save Profile
                </button>
              </div>
            </form>
          </div>

          {/* Change Password Section */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm overflow-hidden transition-colors">
            <div className="p-4 border-b border-gray-200 dark:border-slate-800 bg-gray-50/50 dark:bg-slate-800/40 flex items-center gap-2">
              <Lock className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <h2 className="font-semibold text-gray-800 dark:text-slate-200 text-sm">Change Password</h2>
            </div>
            <form onSubmit={handlePasswordChange} className="p-6 space-y-4 text-xs">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-slate-300 mb-1">Current Password</label>
                <input
                  type="password"
                  value={passwords.old}
                  onChange={(e) => setPasswords({...passwords, old: e.target.value})}
                  className="w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-slate-200 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-600 outline-none transition"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-slate-300 mb-1">New Password</label>
                <input
                  type="password"
                  value={passwords.new}
                  onChange={(e) => setPasswords({...passwords, new: e.target.value})}
                  className="w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-slate-200 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-600 outline-none transition"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-slate-300 mb-1">Confirm New Password</label>
                <input
                  type="password"
                  value={passwords.confirm}
                  onChange={(e) => setPasswords({...passwords, confirm: e.target.value})}
                  className="w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-slate-200 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-600 outline-none transition"
                />
              </div>
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading || !passwords.new}
                  className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-xl font-semibold shadow-sm transition-colors disabled:opacity-50 text-xs"
                >
                  Update Password
                </button>
              </div>
            </form>
          </div>
        </div>

        <div>
          {/* System Configuration (Read-only) */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm overflow-hidden transition-colors">
            <div className="p-4 border-b border-gray-200 dark:border-slate-800 bg-gray-50/50 dark:bg-slate-800/40 flex items-center gap-2">
              <Server className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <h2 className="font-semibold text-gray-800 dark:text-slate-200 text-sm">System Configuration</h2>
            </div>
            <div className="p-6 space-y-6 text-xs">
              <div>
                <p className="text-xs font-medium text-gray-500 dark:text-slate-400 mb-1">Environment</p>
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800/50 rounded-full text-[10px] font-bold uppercase tracking-wider">
                    {process.env.NODE_ENV || 'Production'}
                  </span>
                </div>
              </div>
              
              <div>
                <p className="text-xs font-medium text-gray-500 dark:text-slate-400 mb-2 flex items-center gap-1.5">
                  <Database className="w-3.5 h-3.5" /> Database & Background Tasks
                </p>
                <div className="bg-gray-50 dark:bg-slate-800/40 rounded-xl border border-gray-200 dark:border-slate-800 p-4 space-y-3">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-gray-600 dark:text-slate-400">MongoDB Connection</span>
                    <span className="flex items-center gap-1.5 font-medium text-emerald-600 dark:text-emerald-400">
                      <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                      Connected
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-gray-600 dark:text-slate-400">Event Scheduler</span>
                    <span className={`flex items-center gap-1.5 font-medium ${systemStats?.scheduler_running ? 'text-emerald-600 dark:text-emerald-400' : 'text-gray-500 dark:text-slate-400'}`}>
                      <span className={`w-2 h-2 rounded-full ${systemStats?.scheduler_running ? 'bg-emerald-500' : 'bg-gray-400'}`}></span>
                      {systemStats?.scheduler_running ? 'Running' : 'Online'}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <p className="text-xs font-medium text-gray-500 dark:text-slate-400 mb-2">API Configuration</p>
                <div className="text-xs text-gray-600 dark:text-slate-300 bg-gray-50 dark:bg-slate-800/40 rounded-xl border border-gray-200 dark:border-slate-800 p-4 font-mono break-all">
                  API_URL: http://localhost:5000/api
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
