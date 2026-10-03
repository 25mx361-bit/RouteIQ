/**
 * frontend/src/components/ProtectedRoute.jsx
 * Redirects unauthenticated users to /login.
 * Redirects non-admins away from /admin/* routes.
 */
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { isLoggedIn, isAdmin } from '../services/auth';

export default function ProtectedRoute({ children, requireAdmin = false }) {
  const location = useLocation();

  if (!isLoggedIn()) {
    return <Navigate to="/dashboard" state={{ from: location }} replace />;
  }

  if (requireAdmin && !isAdmin()) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}
