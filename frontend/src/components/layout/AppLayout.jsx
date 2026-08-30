/**
 * frontend/src/components/layout/AppLayout.jsx
 * User layout: Sidebar + AppHeader + <Outlet />
 */
import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import AppHeader from './AppHeader';

const PAGE_TITLES = {
  '/dashboard':      'Dashboard',
  '/plan':           'Plan Route',
  '/predictions':    'Traffic Predictions',
  '/recommendations':'Route Recommendations',
  '/map':            'Route Map',
  '/history':        'Search History',
  '/favorites':      'Favorites',
  '/profile':        'Profile & Settings',
};

export default function AppLayout() {
  const { pathname } = useLocation();
  const title = PAGE_TITLES[pathname] || 'RouteIQ';

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-slate-950 text-gray-900 dark:text-slate-100 transition-colors duration-200">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        <AppHeader title={title} />
        <main className="flex-1 overflow-y-auto bg-gray-50 dark:bg-slate-950">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
