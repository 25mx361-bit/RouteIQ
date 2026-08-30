/**
 * frontend/src/components/layout/AdminSidebar.jsx
 * Admin sidebar with dark/light mode integration.
 */
import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Users, Database, Brain, TrendingUp,
  Map, BarChart2, Settings, LogOut, Menu, X,
  Navigation, Wifi, AlertTriangle, Calendar, Shield,
} from 'lucide-react';
import { clearSession, getUser } from '../../services/auth';

const ADMIN_NAV = [
  { label: 'Dashboard',        icon: LayoutDashboard, to: '/admin' },
  { label: 'User Management',  icon: Users,           to: '/admin/users' },
  { label: 'Traffic Data',     icon: Database,        to: '/admin/traffic' },
  { label: 'ML Models',        icon: Brain,           to: '/admin/models' },
  { label: 'Predictions',      icon: TrendingUp,      to: '/admin/predictions' },
  { label: 'Routes & API',     icon: Map,             to: '/admin/routes' },
  { label: 'API Status',       icon: Wifi,            to: '/admin/api-status' },
  { label: 'Events',           icon: Calendar,        to: '/admin/events' },
  { label: 'Landslides',       icon: AlertTriangle,   to: '/admin/landslides' },
  { label: 'Reports',          icon: BarChart2,       to: '/admin/reports' },
  { label: 'System Logs',      icon: Settings,        to: '/admin/logs' },
  { label: 'Settings',         icon: Settings,        to: '/admin/settings' },
];

export default function AdminSidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const user = getUser();

  const handleLogout = () => {
    clearSession();
    navigate('/login');
  };

  return (
    <aside
      className={`flex flex-col bg-indigo-700 dark:bg-slate-900 text-white transition-all duration-300 ease-in-out
        ${collapsed ? 'w-16' : 'w-60'} min-h-screen shrink-0 shadow-xl border-r border-indigo-600/40 dark:border-slate-800`}
    >
      {/* Logo */}
      <div className="flex items-center justify-between px-4 py-4 border-b border-indigo-600/40 dark:border-slate-800">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-white dark:bg-indigo-600 rounded-lg flex items-center justify-center shadow">
              <Shield className="w-4 h-4 text-indigo-600 dark:text-white" />
            </div>
            <div>
              <p className="font-extrabold text-base leading-tight">RouteIQ</p>
              <p className="text-indigo-300 dark:text-slate-400 text-[9px] font-mono uppercase tracking-wider">Admin Panel</p>
            </div>
          </div>
        )}
        <button onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg hover:bg-indigo-600 dark:hover:bg-slate-800 transition-colors ml-auto text-indigo-100 dark:text-slate-400">
          {collapsed ? <Menu className="w-4 h-4" /> : <X className="w-4 h-4" />}
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto">
        {ADMIN_NAV.map(({ label, icon: Icon, to }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/admin'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all
              ${isActive
                ? 'bg-white dark:bg-indigo-600 text-indigo-700 dark:text-white shadow-sm font-semibold'
                : 'text-indigo-200 dark:text-slate-400 hover:bg-indigo-600/60 dark:hover:bg-slate-800/80 hover:text-white'
              }`
            }
          >
            <Icon className="w-4 h-4 shrink-0" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* User info + Logout */}
      <div className="border-t border-indigo-600/40 dark:border-slate-800 px-2 py-3">
        {!collapsed && user && (
          <div className="flex items-center gap-2 px-3 py-2 mb-1 rounded-lg bg-indigo-800/40 dark:bg-slate-800/50">
            <div className="w-7 h-7 rounded-full bg-indigo-400 dark:bg-indigo-600 flex items-center justify-center text-xs font-bold uppercase">
              {user.name?.[0] || 'A'}
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-semibold truncate text-white">{user.name}</p>
              <p className="text-indigo-300 dark:text-slate-400 text-[9px]">Admin</p>
            </div>
          </div>
        )}
        <button onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-xs font-medium
            text-indigo-200 dark:text-slate-400 hover:bg-indigo-600/60 dark:hover:bg-slate-800/80 hover:text-white transition-all">
          <LogOut className="w-4 h-4 shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
}
