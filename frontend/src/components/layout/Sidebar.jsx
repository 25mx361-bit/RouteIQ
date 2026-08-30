/**
 * frontend/src/components/layout/Sidebar.jsx
 * User sidebar with seamless light (indigo) and dark (deep slate) support.
 */
import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Route, TrendingUp, History,
  Star, Settings, LogOut, Menu, X, Navigation, Compass,
} from 'lucide-react';
import { clearSession, getUser } from '../../services/auth';

const NAV_ITEMS = [
  { label: 'Dashboard',        icon: LayoutDashboard,  to: '/dashboard' },
  { label: 'Plan Route',       icon: Route,            to: '/plan' },
  { label: 'Predictions',      icon: TrendingUp,       to: '/predictions' },
  { label: 'History',          icon: History,          to: '/history' },
  { label: 'Favorites',        icon: Star,             to: '/favorites' },
  { label: 'Settings',         icon: Settings,         to: '/profile' },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const user = getUser();

  const handleLogout = () => {
    clearSession();
    navigate('/login');
  };

  return (
    <aside
      className={`flex flex-col bg-indigo-600 dark:bg-slate-900 text-white transition-all duration-300 ease-in-out
        ${collapsed ? 'w-16' : 'w-64'} min-h-screen shrink-0 shadow-xl border-r border-indigo-500/30 dark:border-slate-800`}
    >
      {/* Logo */}
      <div className="flex items-center justify-between px-4 py-5 border-b border-indigo-500/40 dark:border-slate-800">
        {!collapsed && (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white dark:bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
              <Compass className="w-6 h-6 text-indigo-600 dark:text-white" />
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight text-white block leading-none">
                Route<span className="text-indigo-200">IQ</span>
              </span>
              <span className="text-[10px] uppercase font-mono tracking-widest text-indigo-200 dark:text-slate-400">
                Smart Traffic System
              </span>
            </div>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg hover:bg-indigo-500 dark:hover:bg-slate-800 transition-colors ml-auto text-indigo-100 dark:text-slate-400"
        >
          {collapsed ? <Menu className="w-5 h-5" /> : <X className="w-4 h-4" />}
        </button>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 px-2 py-4 space-y-1">
        {NAV_ITEMS.map(({ label, icon: Icon, to }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all
              ${isActive
                ? 'bg-white dark:bg-indigo-600 text-indigo-700 dark:text-white shadow-sm font-semibold'
                : 'text-indigo-100 dark:text-slate-400 hover:bg-indigo-500/60 dark:hover:bg-slate-800/80 hover:text-white'
              }`
            }
          >
            <Icon className="w-5 h-5 shrink-0" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* User + Logout or Sign In */}
      <div className="border-t border-indigo-500/40 dark:border-slate-800 px-2 py-4 space-y-1">
        {user ? (
          <>
            {!collapsed && (
              <div className="flex items-center gap-3 px-3 py-2 mb-2 rounded-xl bg-indigo-700/40 dark:bg-slate-800/50">
                <div className="w-8 h-8 rounded-full bg-indigo-400 dark:bg-indigo-600 flex items-center justify-center text-sm font-bold uppercase shrink-0">
                  {user.name?.[0] || 'U'}
                </div>
                <div className="overflow-hidden">
                  <p className="text-sm font-semibold truncate text-white">{user.name}</p>
                  <p className="text-indigo-200 dark:text-slate-400 text-[10px] truncate">{user.email}</p>
                </div>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium
                text-indigo-100 dark:text-slate-400 hover:bg-indigo-500/60 dark:hover:bg-slate-800/80 hover:text-white transition-all"
            >
              <LogOut className="w-5 h-5 shrink-0" />
              {!collapsed && <span>Logout</span>}
            </button>
          </>
        ) : (
          <button
            onClick={() => navigate('/login')}
            className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-bold
              bg-white text-indigo-700 dark:bg-indigo-600 dark:text-white hover:bg-indigo-50 dark:hover:bg-indigo-500 transition-all shadow-md"
          >
            <Navigation className="w-5 h-5 shrink-0" />
            {!collapsed && <span>Sign In / Sign Up</span>}
          </button>
        )}
      </div>
    </aside>
  );
}
