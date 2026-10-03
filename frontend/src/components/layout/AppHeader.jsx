/**
 * frontend/src/components/layout/AppHeader.jsx
 * Top header bar — live status indicator, real-time clock, theme toggle, notification bell + user auth controls.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Sun, Moon, Radio, Activity, Clock, LogIn, UserPlus, Shield, LogOut } from 'lucide-react';
import { getUser, isLoggedIn, isAdmin, clearSession } from '../../services/auth';
import { useTheme } from '../../contexts/ThemeContext';
import NotificationPanel from '../NotificationPanel';

export default function AppHeader({ title }) {
  const navigate = useNavigate();
  const [user, setUser] = useState(getUser());
  const [loggedIn, setLoggedIn] = useState(isLoggedIn());
  const adminUser = user?.role === 'admin';
  const { theme, toggleTheme, isDark } = useTheme();
  const [time, setTime] = useState(new Date());

  // Keep auth state reactive to logins and logouts
  useEffect(() => {
    const handleAuth = () => {
      setUser(getUser());
      setLoggedIn(isLoggedIn());
    };
    window.addEventListener('authChange', handleAuth);
    window.addEventListener('storage', handleAuth);
    return () => {
      window.removeEventListener('authChange', handleAuth);
      window.removeEventListener('storage', handleAuth);
    };
  }, []);

  const handleLogout = () => {
    clearSession();
    navigate('/dashboard');
  };

  // Real-time clock
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="h-16 shrink-0 bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-800 px-6 flex items-center justify-between shadow-sm z-10 transition-colors duration-200">
      <div className="flex items-center gap-4">
        <h1 className="text-lg font-bold text-gray-800 dark:text-slate-100 tracking-tight">{title}</h1>

        {/* Real-Time Live Feed indicator */}
        <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800 text-[11px] font-semibold text-emerald-700 dark:text-emerald-400">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="font-mono uppercase tracking-wider text-[10px]">LIVE TELEMETRY</span>
        </div>

        {/* Real-Time Clock */}
        <div className="hidden lg:flex items-center gap-1.5 text-xs text-gray-500 dark:text-slate-400 font-mono">
          <Clock className="w-3.5 h-3.5 text-indigo-500" />
          <span>{time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Dark / Light Mode Toggle Button */}
        <button
          onClick={toggleTheme}
          title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
          aria-label="Toggle theme"
          className="p-2 rounded-xl bg-gray-100 dark:bg-slate-800 text-gray-600 dark:text-amber-400 hover:bg-gray-200 dark:hover:bg-slate-700 transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          {isDark ? (
            <Sun className="w-4 h-4 animate-spin-slow" />
          ) : (
            <Moon className="w-4 h-4 text-indigo-600" />
          )}
        </button>

        {/* Notifications */}
        <NotificationPanel />

        {/* User Auth or Sign In Button */}
        {loggedIn ? (
          <div className="flex items-center gap-2 ml-1 pl-2 border-l border-gray-200 dark:border-slate-800">
            <Link to={adminUser ? "/admin" : "/profile"} className="flex items-center gap-2 hover:opacity-80 transition">
              <div className="w-9 h-9 rounded-full bg-indigo-100 dark:bg-indigo-950 flex items-center justify-center
                text-indigo-700 dark:text-indigo-300 font-bold text-sm uppercase border-2 border-indigo-300 dark:border-indigo-700 shadow-sm">
                {user?.name?.[0] || 'U'}
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-sm font-semibold text-gray-800 dark:text-slate-200 leading-tight truncate max-w-[120px]">{user?.name}</p>
                <p className="text-[10px] text-gray-400 dark:text-slate-500 leading-tight capitalize">{user?.role || 'User'}</p>
              </div>
            </Link>
            <button
              onClick={handleLogout}
              title="Log Out (Return to Dashboard)"
              className="p-2 rounded-xl text-gray-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition ml-0.5"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2 ml-1 pl-2 border-l border-gray-200 dark:border-slate-800">
            <Link 
              to="/login" 
              className="px-3.5 py-1.5 rounded-xl bg-indigo-50 dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-100 dark:hover:bg-slate-700 text-xs font-bold transition flex items-center gap-1.5"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Sign In</span>
            </Link>
            <Link 
              to="/login" 
              className="hidden sm:flex px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition items-center gap-1.5 shadow-md shadow-indigo-500/20"
            >
              <UserPlus className="w-3.5 h-3.5" />
              <span>Register</span>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
}
