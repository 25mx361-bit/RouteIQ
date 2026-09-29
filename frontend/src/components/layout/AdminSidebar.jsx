/**
 * frontend/src/components/layout/AdminSidebar.jsx
 * Admin sidebar with dark/light mode integration.
 */
import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Calendar,
  AlertTriangle,
  BarChart2,
  LogOut,
  Menu,
  X,
  Shield,
} from 'lucide-react';
import { clearSession, getUser } from '../../services/auth';

const ADMIN_NAV = [
  { label: 'Dashboard',       icon: LayoutDashboard, to: '/admin' },
  { label: 'User Management', icon: Users,           to: '/admin/users' },
  { label: 'Events',          icon: Calendar,        to: '/admin/events' },
  { label: 'Landslides',      icon: AlertTriangle,   to: '/admin/landslides' },
  { label: 'Reports',         icon: BarChart2,       to: '/admin/reports' },
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
      className={`flex flex-col bg-white dark:bg-slate-900 text-gray-800 dark:text-white transition-all duration-300 ease-in-out
        ${collapsed ? 'w-16' : 'w-60'} min-h-screen shrink-0 shadow-lg border-r border-gray-200 dark:border-slate-800`}
    >
      {/* Logo */}
      <div className="flex items-center justify-between px-4 py-4 border-b border-gray-100 dark:border-slate-800">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-indigo-600 text-white rounded-lg flex items-center justify-center shadow">
              <Shield className="w-4 h-4" />
            </div>
            <div>
              <p className="font-extrabold text-base leading-tight text-gray-900 dark:text-white">RouteIQ</p>
              <p className="text-indigo-600 dark:text-slate-400 text-[9px] font-mono uppercase tracking-wider">Admin Panel</p>
            </div>
          </div>
        )}
        <button onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors ml-auto text-gray-400 dark:text-slate-400">
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
              `flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all
              ${isActive
                ? 'bg-indigo-50 dark:bg-indigo-600 text-indigo-700 dark:text-white shadow-sm font-bold'
                : 'text-gray-600 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-slate-800/80 hover:text-gray-900 dark:hover:text-white'
              }`
            }
          >
            <Icon className="w-4 h-4 shrink-0" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* User info + Logout */}
      <div className="border-t border-gray-100 dark:border-slate-800 px-2 py-3">
        {!collapsed && user && (
          <div className="flex items-center gap-2 px-3 py-2 mb-1 rounded-xl bg-gray-50 dark:bg-slate-800/50 border border-gray-200 dark:border-slate-800">
            <div className="w-7 h-7 rounded-full bg-indigo-100 dark:bg-indigo-600 text-indigo-700 dark:text-white flex items-center justify-center text-xs font-bold uppercase">
              {user.name?.[0] || 'A'}
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-semibold truncate text-gray-900 dark:text-white">{user.name}</p>
              <p className="text-gray-500 dark:text-slate-400 text-[9px]">Admin</p>
            </div>
          </div>
        )}
        <button onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2 rounded-xl text-xs font-medium
            text-gray-600 dark:text-slate-400 hover:bg-rose-50 dark:hover:bg-rose-950/30 hover:text-rose-600 dark:hover:text-rose-400 transition-all">
          <LogOut className="w-4 h-4 shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
}
