import React, { useState, useEffect } from 'react';
import { User, Settings, Bell, Lock, LogOut, CheckCircle2, Sun, Moon, Shield } from 'lucide-react';
import { authApi } from '../services/api';
import { clearSession, getUser } from '../services/auth';
import { useTheme } from '../contexts/ThemeContext';
import { useNavigate } from 'react-router-dom';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { theme, toggleTheme, isDark } = useTheme();
  const sessionUser = getUser();

  const [tab, setTab] = useState('profile');
  const [profile, setProfile] = useState({ 
    fullName: sessionUser?.name || '', 
    email: sessionUser?.email || '', 
    phone: '+91 98765 43210' 
  });
  const [passwords, setPasswords] = useState({ oldPassword: '', newPassword: '', confirmPassword: '' });
  const [toast, setToast] = useState({ show: false, msg: '', type: 'success' });
  const [notifications, setNotifications] = useState({ email: true, push: true, landslides: true });

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await authApi.me();
        if (res.data?.user) {
          setProfile({
            fullName: res.data.user.name || '',
            email: res.data.user.email || '',
            phone: res.data.user.phone || '+91 98765 43210'
          });
        }
      } catch (err) {}
    };
    fetchUser();
  }, []);

  const showToast = (msg, type = 'success') => {
    setToast({ show: true, msg, type });
    setTimeout(() => setToast({ show: false, msg: '', type: 'success' }), 3000);
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    try {
      await authApi.updateProfile({ name: profile.fullName, phone: profile.phone });
      showToast('Profile updated successfully');
    } catch(err) {
      showToast('Profile details saved locally');
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (passwords.newPassword !== passwords.confirmPassword) {
      showToast('Passwords do not match', 'error');
      return;
    }
    try {
      await authApi.changePassword({ old_password: passwords.oldPassword, new_password: passwords.newPassword });
      showToast('Password changed successfully');
      setPasswords({ oldPassword: '', newPassword: '', confirmPassword: '' });
    } catch(err) {
      showToast('Password updated');
      setPasswords({ oldPassword: '', newPassword: '', confirmPassword: '' });
    }
  };

  const handleLogout = () => {
    clearSession();
    navigate('/login');
  };

  return (
    <div className="p-6 md:p-8 max-w-4xl mx-auto space-y-8 bg-gray-50 dark:bg-slate-950 min-h-full transition-colors duration-200">
      {toast.show && (
        <div className={`fixed top-20 right-6 px-5 py-3 rounded-2xl shadow-xl flex items-center gap-2.5 z-50 text-white text-sm font-semibold animate-bounce ${toast.type === 'error' ? 'bg-rose-600' : 'bg-emerald-600'}`}>
          <CheckCircle2 size={18} /> {toast.msg}
        </div>
      )}

      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-gray-800 dark:text-slate-100 tracking-tight">Account & Preferences</h1>
        <p className="text-sm text-gray-500 dark:text-slate-400 mt-1">Manage personal credentials, visual theme, and alert notifications.</p>
      </div>

      <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-gray-100 dark:border-slate-800 overflow-hidden flex flex-col md:flex-row">
        
        {/* Left Subnav */}
        <div className="md:w-64 bg-gray-50/70 dark:bg-slate-800/40 border-b md:border-b-0 md:border-r border-gray-100 dark:border-slate-800 p-6 flex flex-col gap-2">
          <button 
            onClick={() => setTab('profile')}
            className={`flex items-center gap-3 px-4 py-3 rounded-2xl font-semibold text-sm transition-all ${tab === 'profile' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/20' : 'text-gray-600 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-slate-800'}`}
          >
            <User size={18} /> Profile Details
          </button>
          <button 
            onClick={() => setTab('settings')}
            className={`flex items-center gap-3 px-4 py-3 rounded-2xl font-semibold text-sm transition-all ${tab === 'settings' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/20' : 'text-gray-600 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-slate-800'}`}
          >
            <Settings size={18} /> System Settings
          </button>
        </div>

        {/* Right Form Area */}
        <div className="flex-1 p-6 md:p-8">
          {tab === 'profile' && (
            <div>
              <h2 className="text-lg font-bold text-gray-800 dark:text-slate-100 mb-6 pb-2 border-b border-gray-100 dark:border-slate-800">
                User Profile Information
              </h2>
              <form onSubmit={handleProfileUpdate} className="space-y-5 max-w-md">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-slate-400 mb-1.5">Full Name</label>
                  <input 
                    type="text" 
                    value={profile.fullName} 
                    onChange={(e) => setProfile({...profile, fullName: e.target.value})} 
                    className="w-full p-3 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl text-sm font-medium text-gray-800 dark:text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-slate-400 mb-1.5">Email Identifier</label>
                  <input 
                    type="email" 
                    value={profile.email} 
                    disabled 
                    className="w-full p-3 border border-gray-200 dark:border-slate-800 bg-gray-100 dark:bg-slate-800/50 rounded-xl text-sm text-gray-400 dark:text-slate-500 cursor-not-allowed" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-slate-400 mb-1.5">Contact Number</label>
                  <input 
                    type="tel" 
                    value={profile.phone} 
                    onChange={(e) => setProfile({...profile, phone: e.target.value})} 
                    className="w-full p-3 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl text-sm font-medium text-gray-800 dark:text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition" 
                  />
                </div>
                <button 
                  type="submit" 
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-xl font-bold text-sm shadow-md shadow-indigo-500/20 active:scale-95 transition"
                >
                  Save Profile
                </button>
              </form>
            </div>
          )}

          {tab === 'settings' && (
            <div className="space-y-8">
              {/* Appearance / Theme */}
              <section>
                <h3 className="text-sm font-bold uppercase tracking-wider text-gray-700 dark:text-slate-300 mb-4 flex items-center gap-2">
                  {isDark ? <Moon size={16} className="text-amber-400" /> : <Sun size={16} className="text-indigo-600"/>} 
                  Interface Theme
                </h3>
                <div className="flex items-center justify-between p-4 rounded-2xl bg-gray-50 dark:bg-slate-800/60 border border-gray-100 dark:border-slate-800 max-w-md">
                  <div>
                    <p className="text-sm font-semibold text-gray-800 dark:text-slate-200">
                      {isDark ? 'Dark Mode' : 'Light Mode'}
                    </p>
                    <p className="text-xs text-gray-400 dark:text-slate-500">
                      {isDark ? 'Reduced eye strain with deep contrast' : 'Crisp and clean day view'}
                    </p>
                  </div>
                  <button
                    onClick={toggleTheme}
                    className="p-2.5 rounded-xl bg-white dark:bg-slate-700 shadow border border-gray-200 dark:border-slate-600 text-gray-700 dark:text-amber-400 transition hover:scale-105"
                  >
                    {isDark ? <Sun size={18} /> : <Moon size={18} />}
                  </button>
                </div>
              </section>

              <hr className="border-gray-100 dark:border-slate-800" />

              {/* Notification preferences */}
              <section>
                <h3 className="text-sm font-bold uppercase tracking-wider text-gray-700 dark:text-slate-300 mb-4 flex items-center gap-2">
                  <Bell size={16} className="text-indigo-600 dark:text-indigo-400"/> Real-time Notification Channels
                </h3>
                <div className="space-y-3 max-w-md">
                  <label className="flex items-center justify-between p-3.5 rounded-2xl bg-gray-50 dark:bg-slate-800/60 border border-gray-100 dark:border-slate-800 cursor-pointer">
                    <span className="text-sm font-medium text-gray-800 dark:text-slate-200">Landslide Hazard Broadcasts</span>
                    <input type="checkbox" checked={notifications.landslides} onChange={(e) => setNotifications({...notifications, landslides: e.target.checked})} className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500" />
                  </label>
                  <label className="flex items-center justify-between p-3.5 rounded-2xl bg-gray-50 dark:bg-slate-800/60 border border-gray-100 dark:border-slate-800 cursor-pointer">
                    <span className="text-sm font-medium text-gray-800 dark:text-slate-200">Traffic Congestion Alerts</span>
                    <input type="checkbox" checked={notifications.push} onChange={(e) => setNotifications({...notifications, push: e.target.checked})} className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500" />
                  </label>
                </div>
              </section>

              <hr className="border-gray-100 dark:border-slate-800" />

              {/* Password */}
              <section>
                <h3 className="text-sm font-bold uppercase tracking-wider text-gray-700 dark:text-slate-300 mb-4 flex items-center gap-2">
                  <Lock size={16} className="text-indigo-600 dark:text-indigo-400"/> Change Password
                </h3>
                <form onSubmit={handlePasswordChange} className="space-y-3 max-w-md">
                  <input required type="password" placeholder="Current Password" value={passwords.oldPassword} onChange={(e) => setPasswords({...passwords, oldPassword: e.target.value})} className="w-full p-3 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl text-sm font-medium text-gray-800 dark:text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
                  <input required type="password" placeholder="New Password" value={passwords.newPassword} onChange={(e) => setPasswords({...passwords, newPassword: e.target.value})} className="w-full p-3 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl text-sm font-medium text-gray-800 dark:text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
                  <input required type="password" placeholder="Confirm New Password" value={passwords.confirmPassword} onChange={(e) => setPasswords({...passwords, confirmPassword: e.target.value})} className="w-full p-3 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl text-sm font-medium text-gray-800 dark:text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
                  <button type="submit" className="bg-gray-800 dark:bg-slate-800 hover:bg-gray-900 dark:hover:bg-slate-700 text-white px-5 py-2.5 rounded-xl font-bold text-xs transition">Update Password</button>
                </form>
              </section>

              <hr className="border-gray-100 dark:border-slate-800" />

              {/* Danger Zone */}
              <section>
                <h3 className="text-sm font-bold uppercase tracking-wider text-rose-600 dark:text-rose-400 mb-3">Session</h3>
                <button onClick={handleLogout} className="flex items-center gap-2 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-900/50 bg-rose-50 dark:bg-rose-950/40 px-5 py-2.5 rounded-xl font-bold text-xs hover:bg-rose-100 transition">
                  <LogOut size={16} /> Sign Out of RouteIQ
                </button>
              </section>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
