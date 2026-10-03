/**
 * frontend/src/components/layout/Sidebar.jsx
 * User sidebar with seamless light (indigo) and dark (deep slate) support.
 */
import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Route, TrendingUp, History,
  Star, Settings, LogOut, Menu, X, Navigation, Compass,
  Activity, ShieldCheck, Shield
} from 'lucide-react';
import { clearSession, getUser, isAdmin } from '../../services/auth';

const NAV_ITEMS = [
  { label: 'Dashboard',           icon: LayoutDashboard, to: '/dashboard' },
  { label: 'Plan Route',          icon: Route,           to: '/plan' },
  { label: 'Predictions',         icon: TrendingUp,      to: '/predictions' },
  { label: 'Recommendations',     icon: ShieldCheck,     to: '/recommendations' },
  { label: 'Forecast Validation', icon: Activity,        to: '/forecast-validation' },
  { label: 'History',             icon: History,         to: '/history' },
  { label: 'Favorites',           icon: Star,            to: '/favorites' },
  { label: 'Settings',            icon: Settings,        to: '/profile' },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const [user, setUser] = useState(getUser());

  React.useEffect(() => {
    const handleAuth = () => setUser(getUser());
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

  return (
    <aside
      className={`flex flex-col bg-white dark:bg-slate-900 text-gray-800 dark:text-white transition-all duration-300 ease-in-out
        ${collapsed ? 'w-16' : 'w-64'} min-h-screen shrink-0 shadow-lg border-r border-gray-200 dark:border-slate-800`}
    >
      {/* Logo */}
      <div className="flex items-center justify-between px-4 py-5 border-b border-gray-100 dark:border-slate-800">
        {!collapsed && (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-600 text-white rounded-xl flex items-center justify-center shadow-md">
              <Compass className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight text-gray-900 dark:text-white block leading-none">
                Route<span className="text-indigo-600 dark:text-indigo-400">IQ</span>
              </span>
              <span className="text-[10px] uppercase font-mono tracking-widest text-indigo-600 dark:text-slate-400">
                Smart Traffic System
              </span>
            </div>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors ml-auto text-gray-400 dark:text-slate-400"
        >
          {collapsed ? <Menu className="w-5 h-5" /> : <X className="w-4 h-4" />}
        </button>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 px-2.5 py-4 space-y-1">
        {NAV_ITEMS.map(({ label, icon: Icon, to }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all
              ${isActive
                ? 'bg-indigo-50 dark:bg-indigo-600 text-indigo-700 dark:text-white shadow-sm font-bold'
                : 'text-gray-600 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-slate-800/80 hover:text-gray-900 dark:hover:text-white'
              }`
            }
          >
            <Icon className="w-5 h-5 shrink-0" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* User + Logout or Sign In */}
      <div className="border-t border-gray-100 dark:border-slate-800 px-2.5 py-4 space-y-1">
        {user ? (
          <>
            {!collapsed && (
              <div className="flex items-center gap-3 px-3 py-2 mb-2 rounded-xl bg-gray-50 dark:bg-slate-800/50 border border-gray-200/80 dark:border-slate-800">
                <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-600 text-indigo-700 dark:text-white flex items-center justify-center text-sm font-bold uppercase shrink-0">
                  {user.name?.[0] || 'U'}
                </div>
                <div className="overflow-hidden">
                  <p className="text-sm font-semibold truncate text-gray-900 dark:text-white">{user.name}</p>
                  <p className="text-gray-500 dark:text-slate-400 text-[10px] truncate">{user.email}</p>
                </div>
              </div>
            )}
            {isAdmin() && (
              <NavLink
                to="/admin"
                className="flex items-center gap-3 w-full px-3 py-2 rounded-xl text-xs font-semibold
                  text-amber-700 dark:text-amber-200 bg-amber-50 dark:bg-amber-500/20 hover:bg-amber-100 dark:hover:bg-amber-500/30 border border-amber-200 dark:border-amber-400/30 transition-all mb-1"
              >
                <Shield className="w-4 h-4 shrink-0 text-amber-600 dark:text-amber-300" />
                {!collapsed && <span>Admin Console</span>}
              </NavLink>
            )}
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium
                text-gray-600 dark:text-slate-400 hover:bg-rose-50 dark:hover:bg-rose-950/30 hover:text-rose-600 dark:hover:text-rose-400 transition-all"
            >
              <LogOut className="w-5 h-5 shrink-0" />
              {!collapsed && <span>Logout</span>}
            </button>
          </>
        ) : (
          <button
            onClick={() => navigate('/login')}
            className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-bold
              bg-indigo-600 hover:bg-indigo-700 text-white transition-all shadow-md"
          >
            <Navigation className="w-5 h-5 shrink-0" />
            {!collapsed && <span>Sign In / Sign Up</span>}
          </button>
        )}
      </div>
    </aside>
  );
}
