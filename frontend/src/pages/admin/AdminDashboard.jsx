import React, { useState, useEffect } from 'react';
import {
  Users,
  Database,
  Calendar,
  AlertTriangle,
  Activity,
  ArrowLeft,
  Settings,
  ShieldAlert
} from 'lucide-react';
import { adminApi } from '../../services/api';

export default function AdminDashboard({ onBackToDashboard, onNavigate }) {
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
      setStats(res.data.stats);
    } catch (err) {
      setError(err.message || 'Failed to fetch admin stats');
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon: Icon, colorClass, onClick }) => (
    <div
      onClick={onClick}
      className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center gap-4 hover:bg-slate-800/80 cursor-pointer transition-all"
    >
      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${colorClass}`}>
        <Icon className="w-6 h-6" />
      </div>
      <div>
        <p className="text-slate-400 text-sm">{title}</p>
        <p className="text-2xl font-bold text-slate-100">{value ?? '-'}</p>
      </div>
    </div>
  );

  return (
    <div className="flex flex-col h-screen bg-slate-950 text-slate-100 overflow-y-auto">
      {/* Header */}
      <header className="shrink-0 h-16 bg-slate-900/80 backdrop-blur border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-4">
          <button
            onClick={onBackToDashboard}
            className="p-2 -ml-2 rounded-lg hover:bg-slate-800 text-slate-400 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-lg font-bold">Admin Dashboard</h1>
            <p className="text-xs text-slate-400">System overview and management</p>
          </div>
        </div>
      </header>

      <div className="max-w-6xl w-full mx-auto p-6 space-y-6">
        {error && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-sm">
            {error}
          </div>
        )}

        {/* Top Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          <StatCard
            title="Total Users"
            value={stats?.total_users}
            icon={Users}
            colorClass="bg-blue-500/20 text-blue-400"
            onClick={() => onNavigate('ADMIN_USERS')}
          />
          <StatCard
            title="Active Events"
            value={stats?.active_events}
            icon={Calendar}
            colorClass="bg-purple-500/20 text-purple-400"
            onClick={() => onNavigate('ADMIN_EVENTS')}
          />
          <StatCard
            title="Active Landslides"
            value={stats?.active_landslides}
            icon={AlertTriangle}
            colorClass="bg-rose-500/20 text-rose-400"
            onClick={() => onNavigate('ADMIN_LANDSLIDES')}
          />
          <StatCard
            title="Routes Today"
            value={stats?.routes_searched_today}
            icon={Database}
            colorClass="bg-emerald-500/20 text-emerald-400"
            onClick={() => onNavigate('ADMIN_LOGS')}
          />
          <StatCard
            title="Scheduler"
            value={stats?.scheduler_running ? 'Running' : 'Stopped'}
            icon={Activity}
            colorClass={stats?.scheduler_running ? 'bg-teal-500/20 text-teal-400' : 'bg-slate-500/20 text-slate-400'}
            onClick={() => {}}
          />
        </div>

        {/* Navigation Grid */}
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 pt-4">
          Management Modules
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            onClick={() => onNavigate('ADMIN_USERS')}
            className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-blue-500/50 cursor-pointer group transition-all"
          >
            <Users className="w-8 h-8 text-blue-400 mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-lg font-bold mb-1">User Management</h3>
            <p className="text-sm text-slate-400">Manage user roles, deactivate accounts, and view user list.</p>
          </div>

          <div
            onClick={() => onNavigate('ADMIN_MODELS')}
            className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-emerald-500/50 cursor-pointer group transition-all"
          >
            <Database className="w-8 h-8 text-emerald-400 mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-lg font-bold mb-1">ML Models</h3>
            <p className="text-sm text-slate-400">View PatchTST and CatBoost metrics, and trigger training jobs.</p>
          </div>

          <div
            onClick={() => onNavigate('ADMIN_LOGS')}
            className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-purple-500/50 cursor-pointer group transition-all"
          >
            <Settings className="w-8 h-8 text-purple-400 mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-lg font-bold mb-1">System Logs</h3>
            <p className="text-sm text-slate-400">View API and system audit logs with filtering.</p>
          </div>

          <div
            onClick={() => onNavigate('ADMIN_EVENTS')}
            className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-amber-500/50 cursor-pointer group transition-all"
          >
            <Calendar className="w-8 h-8 text-amber-400 mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-lg font-bold mb-1">Events Console</h3>
            <p className="text-sm text-slate-400">Manage festivals, marriages, and public gatherings.</p>
          </div>

          <div
            onClick={() => onNavigate('ADMIN_LANDSLIDES')}
            className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-rose-500/50 cursor-pointer group transition-all"
          >
            <ShieldAlert className="w-8 h-8 text-rose-400 mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-lg font-bold mb-1">Landslides Console</h3>
            <p className="text-sm text-slate-400">Report active landslides and unblock roads.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
