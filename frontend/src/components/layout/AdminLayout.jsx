/**
 * frontend/src/components/layout/AdminLayout.jsx
 * Admin layout: AdminSidebar + AppHeader + <Outlet />
 */
import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import AdminSidebar from './AdminSidebar';
import AppHeader from './AppHeader';

const ADMIN_TITLES = {
  '/admin':            'Admin Dashboard',
  '/admin/users':      'User Management',
  '/admin/events':     'Events & Tamil Calendar',
  '/admin/landslides': 'Landslides Hazard Management',
  '/admin/reports':    'Reports & Analytics',
};

export default function AdminLayout() {
  const { pathname } = useLocation();
  const title = ADMIN_TITLES[pathname] || 'Admin Panel';

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-slate-950 text-gray-900 dark:text-slate-100 transition-colors duration-200">
      <AdminSidebar />
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        <AppHeader title={title} />
        <main className="flex-1 overflow-y-auto bg-gray-50 dark:bg-slate-950">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
