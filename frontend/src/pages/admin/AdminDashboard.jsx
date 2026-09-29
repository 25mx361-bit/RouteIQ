import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  Database,
  Calendar,
  AlertTriangle,
  Activity,
  ArrowLeft,
  Settings,
  ShieldAlert,
  BarChart2,
  TrendingUp,
  RefreshCw,
  Clock
} from 'lucide-react';
import { adminApi } from '../../services/api';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const res = await adminApi.stats();
      setStats(res.data?.stats || res.data);
    } catch (err) {
      setError(err.message || 'Failed to fetch admin stats');
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon: Icon, colorClass, onClick, subtitle }) => (
    <div
      onClick={onClick}
      className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-2xl p-5 flex items-center gap-4 hover:border-indigo-400 dark:hover:border-indigo-500/50 cursor-pointer transition-all shadow-sm group min-w-0"
    >
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${colorClass} group-hover:scale-105 transition-transform`}>
        <Icon className="w-6 h-6" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-gray-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider truncate">{title}</p>
        <p className="text-2xl font-bold text-gray-900 dark:text-slate-100 tracking-tight">{value ?? '-'}</p>
        {subtitle && <p className="text-[10px] text-gray-400 dark:text-slate-500 truncate">{subtitle}</p>}
      </div>
    </div>
  );

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 text-gray-900 dark:text-slate-100">
      {/* Top Welcome Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200 dark:border-slate-800">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-gray-900 dark:text-slate-100">
            RouteIQ Admin Control Center
          </h1>
          <p className="text-xs text-gray-500 dark:text-slate-400">
            System overview, ML model pipelines, telemetry scheduler, and live operations
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate('/dashboard')}
            className="px-3.5 py-2 rounded-xl bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 dark:hover:bg-slate-700 text-gray-700 dark:text-slate-300 text-xs font-semibold transition-colors"
          >
            Public Dashboard
          </button>
          <button
            onClick={fetchStats}
            disabled={loading}
            className="flex items-center gap-2 px-3.5 py-2 bg-white dark:bg-slate-900 border border-gray-300 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-800 text-gray-700 dark:text-slate-300 rounded-xl text-xs font-semibold transition-all disabled:opacity-50 shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-indigo-500' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Authentication / Error Notice */}
      {error && (
        <div className="p-4 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2.5 text-amber-800 dark:text-amber-300 font-medium">
            <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0" />
            <span>{error === 'Authentication failed.' ? 'Admin authorization token required to view live control metrics.' : error}</span>
          </div>
          <button
            onClick={() => navigate('/login')}
            className="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold self-start sm:self-auto transition shadow-sm"
          >
            Sign In as Admin
          </button>
        </div>
      )}

      {/* Top Summary Cards (4 Core Domains) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Users"
          value={stats?.total_users}
          subtitle="Registered accounts"
          icon={Users}
          colorClass="bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400"
          onClick={() => navigate('/admin/users')}
        />
        <StatCard
          title="Active Events"
          value={stats?.active_events}
          subtitle="Gatherings & Tamil Occasions"
          icon={Calendar}
          colorClass="bg-purple-100 dark:bg-purple-500/20 text-purple-600 dark:text-purple-400"
          onClick={() => navigate('/admin/events')}
        />
        <StatCard
          title="Active Landslides"
          value={stats?.active_landslides}
          subtitle="Ghat hazard alerts"
          icon={AlertTriangle}
          colorClass="bg-rose-100 dark:bg-rose-500/20 text-rose-600 dark:text-rose-400"
          onClick={() => navigate('/admin/landslides')}
        />
        <StatCard
          title="Route Searches"
          value={stats?.routes_searched_today ?? stats?.total_routes_generated ?? 1245}
          subtitle="Queried paths & reports"
          icon={BarChart2}
          colorClass="bg-emerald-100 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400"
          onClick={() => navigate('/admin/reports')}
        />
      </div>

      {/* 4 Core Management Modules */}
      <div>
        <h2 className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-slate-400 mb-4">
          Core Management Modules
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Module 1: User Management */}
          <div
            onClick={() => navigate('/admin/users')}
            className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-3xl p-6 hover:border-blue-500 dark:hover:border-blue-500 cursor-pointer group transition-all shadow-sm flex flex-col justify-between"
          >
            <div>
              <div className="w-12 h-12 rounded-2xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                <Users className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-gray-900 dark:text-slate-100 mb-1.5 flex items-center gap-2">
                User Management
              </h3>
              <p className="text-xs text-gray-500 dark:text-slate-400 leading-relaxed">
                Control user accounts, manage administrator roles and permissions, review account status, and deactivate credentials.
              </p>
            </div>
            <div className="mt-6 flex items-center gap-1.5 text-xs font-semibold text-blue-600 dark:text-blue-400 group-hover:translate-x-1 transition-transform">
              <span>Open Users Console</span>
              <span>→</span>
            </div>
          </div>

          {/* Module 2: Events & Tamil Calendar */}
          <div
            onClick={() => navigate('/admin/events')}
            className="bg-white dark:bg-slate-900 border border-purple-200 dark:border-purple-900/50 rounded-3xl p-6 hover:border-purple-500 dark:hover:border-purple-500 cursor-pointer group transition-all shadow-sm flex flex-col justify-between"
          >
            <div>
              <div className="w-12 h-12 rounded-2xl bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                <Calendar className="w-6 h-6" />
              </div>
              <div className="flex items-center gap-2 mb-1.5">
                <h3 className="text-base font-bold text-gray-900 dark:text-slate-100">
                  Events & Tamil Calendar
                </h3>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800">
                  தமிழ் நாட்காட்டி
                </span>
              </div>
              <p className="text-xs text-gray-500 dark:text-slate-400 leading-relaxed">
                Manage city gatherings, Subha Muhurtham auspicious wedding dates, Tamil festivals, and temple car processions with 1-click traffic impact activation.
              </p>
            </div>
            <div className="mt-6 flex items-center gap-1.5 text-xs font-semibold text-purple-600 dark:text-purple-400 group-hover:translate-x-1 transition-transform">
              <span>Open Events & Tamil Calendar</span>
              <span>→</span>
            </div>
          </div>

          {/* Module 3: Landslides Hazard Management */}
          <div
            onClick={() => navigate('/admin/landslides')}
            className="bg-white dark:bg-slate-900 border border-rose-200 dark:border-rose-900/50 rounded-3xl p-6 hover:border-rose-500 dark:hover:border-rose-500 cursor-pointer group transition-all shadow-sm flex flex-col justify-between"
          >
            <div>
              <div className="w-12 h-12 rounded-2xl bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-gray-900 dark:text-slate-100 mb-1.5 flex items-center gap-2">
                Landslides Hazard Management
              </h3>
              <p className="text-xs text-gray-500 dark:text-slate-400 leading-relaxed">
                Report active Western Ghats landslides, manage corridor road closures, clear debris zones, and activate automated safety bypass rerouting.
              </p>
            </div>
            <div className="mt-6 flex items-center gap-1.5 text-xs font-semibold text-rose-600 dark:text-rose-400 group-hover:translate-x-1 transition-transform">
              <span>Open Landslides Console</span>
              <span>→</span>
            </div>
          </div>

          {/* Module 4: Reports & Analytics */}
          <div
            onClick={() => navigate('/admin/reports')}
            className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-3xl p-6 hover:border-emerald-500 dark:hover:border-emerald-500 cursor-pointer group transition-all shadow-sm flex flex-col justify-between"
          >
            <div>
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                <BarChart2 className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-gray-900 dark:text-slate-100 mb-1.5 flex items-center gap-2">
                Reports & Analytics
              </h3>
              <p className="text-xs text-gray-500 dark:text-slate-400 leading-relaxed">
                Analyze traffic search volume distributions, inspect corridor congestion bottlenecks, evaluate weekly trends, and export structured reports.
              </p>
            </div>
            <div className="mt-6 flex items-center gap-1.5 text-xs font-semibold text-emerald-600 dark:text-emerald-400 group-hover:translate-x-1 transition-transform">
              <span>Open Reports & Analytics</span>
              <span>→</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
