/**
 * frontend/src/App.jsx
 * RouteIQ — Root router. Full SPA with Public Prediction Dashboard & Protected Member Features.
 */
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';

// Layouts
import AppLayout from './components/layout/AppLayout';
import AdminLayout from './components/layout/AdminLayout';
import ProtectedRoute from './components/ProtectedRoute';

// Public Auth Page
import LoginPage from './pages/LoginPage';

// User & Public Prediction Pages
import UserDashboard       from './pages/UserDashboard';
import PlanRoutePage       from './pages/PlanRoutePage';
import PredictionsPage     from './pages/PredictionsPage';
import RecommendationsPage from './pages/RecommendationsPage';
import RouteMapPage        from './pages/RouteMapPage';
import HistoryPage         from './pages/HistoryPage';
import FavoritesPage       from './pages/FavoritesPage';
import ProfilePage         from './pages/ProfilePage';

// Admin pages
import AdminDashboard        from './pages/admin/AdminDashboard';
import UsersPage             from './pages/admin/UsersPage';
import ModelsPage            from './pages/admin/ModelsPage';
import LogsPage              from './pages/admin/LogsPage';
import EventsPage            from './pages/admin/EventsPage';
import LandslidesPage        from './pages/admin/LandslidesPage';
import TrafficDataPage       from './pages/admin/TrafficDataPage';
import PredictionMonitorPage from './pages/admin/PredictionMonitorPage';
import RouteMonitorPage      from './pages/admin/RouteMonitorPage';
import ApiStatusPage         from './pages/admin/ApiStatusPage';
import ReportsPage           from './pages/admin/ReportsPage';
import AdminSettingsPage     from './pages/admin/AdminSettingsPage';

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Authentication */}
          <Route path="/login" element={<LoginPage />} />

          {/* ── Public & User Interactive Platform (AppLayout) ──── */}
          <Route element={<AppLayout />}>
            <Route path="/"               element={<UserDashboard />} />
            <Route path="/dashboard"      element={<UserDashboard />} />
            <Route path="/plan"           element={<PlanRoutePage />} />
            <Route path="/predictions"    element={<PredictionsPage />} />
            <Route path="/recommendations" element={<RecommendationsPage />} />
            <Route path="/map"            element={<RouteMapPage />} />

            {/* Protected Member-Specific Features */}
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <HistoryPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/favorites"
              element={
                <ProtectedRoute>
                  <FavoritesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* ── Protected Admin Control Center (AdminLayout) ───── */}
          <Route
            element={
              <ProtectedRoute requireAdmin>
                <AdminLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/admin"                element={<AdminDashboard />} />
            <Route path="/admin/users"          element={<UsersPage />} />
            <Route path="/admin/traffic"        element={<TrafficDataPage />} />
            <Route path="/admin/models"         element={<ModelsPage />} />
            <Route path="/admin/predictions"    element={<PredictionMonitorPage />} />
            <Route path="/admin/routes"         element={<RouteMonitorPage />} />
            <Route path="/admin/api-status"     element={<ApiStatusPage />} />
            <Route path="/admin/events"         element={<EventsPage />} />
            <Route path="/admin/landslides"     element={<LandslidesPage />} />
            <Route path="/admin/reports"        element={<ReportsPage />} />
            <Route path="/admin/logs"           element={<LogsPage />} />
            <Route path="/admin/settings"       element={<AdminSettingsPage />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
