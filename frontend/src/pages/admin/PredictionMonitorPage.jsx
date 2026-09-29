import React, { useState, useEffect } from 'react';
import { adminApi } from '../../services/api';
import CongestionBadge from '../../components/CongestionBadge';
import { Activity, Clock, AlertTriangle, TrendingUp, RefreshCw, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function PredictionMonitorPage() {
  const navigate = useNavigate();
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [congestionFilter, setCongestionFilter] = useState('');
  const [stats, setStats] = useState({ total: 0, highCongestion: 0, avgTci: 0 });

  useEffect(() => {
    fetchPredictions();
  }, [page, congestionFilter]);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      const res = await adminApi.getPredictionsList({ page, limit: 25, congestion: congestionFilter });
      const preds = res.data?.predictions || [];
      setPredictions(preds);
      setTotalPages(res.data?.pages || 1);

      if (res.data?.stats) {
        setStats(res.data.stats);
      } else if (preds.length > 0) {
        const high = preds.filter(p => (p.congestion_level || '').toLowerCase() === 'high').length;
        const tcis = preds.map(p => p.predicted_tci).filter(t => typeof t === 'number');
        const avg = tcis.length ? tcis.reduce((a, b) => a + b, 0) / tcis.length : 1.0;
        setStats({ total: res.data?.total || preds.length, highCongestion: high, avgTci: avg });
      }
    } catch (err) {
      console.error('Failed to fetch predictions:', err);
    } finally {
      setLoading(false);
    }
  };

  const SummaryCard = ({ title, value, subtitle, icon: Icon, colorClass }) => (
    <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-2xl p-5 flex items-center gap-4 shadow-sm min-w-0">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${colorClass}`}>
        <Icon className="w-6 h-6" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-gray-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider truncate">{title}</p>
        <p className="text-2xl font-bold text-gray-900 dark:text-slate-100 tracking-tight">{value}</p>
        {subtitle && <p className="text-[11px] text-gray-400 dark:text-slate-500 truncate">{subtitle}</p>}
      </div>
    </div>
  );

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 text-gray-900 dark:text-slate-100">
      {/* Header Row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200 dark:border-slate-800">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/admin')}
            className="p-2 rounded-xl bg-white dark:bg-slate-900 hover:bg-gray-100 dark:hover:bg-slate-800 text-gray-600 dark:text-slate-400 border border-gray-200 dark:border-slate-800 transition-colors shadow-sm"
            title="Back to Admin Dashboard"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-gray-900 dark:text-slate-100">Prediction Monitor</h1>
            <p className="text-xs text-gray-500 dark:text-slate-400">Live feed of user route queries, inference results, and congestion index</p>
          </div>
        </div>

        <button
          onClick={fetchPredictions}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 bg-white dark:bg-slate-900 border border-gray-300 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-800 text-gray-700 dark:text-slate-300 rounded-xl text-xs font-semibold transition-all disabled:opacity-50 shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-indigo-500' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <SummaryCard
          title="Total Predictions"
          value={stats.total}
          subtitle="All recorded route forecasts"
          icon={Activity}
          colorClass="bg-indigo-100 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400"
        />
        <SummaryCard
          title="High Congestion"
          value={stats.highCongestion}
          subtitle="Routes with TCI > 1.40"
          icon={AlertTriangle}
          colorClass="bg-rose-100 dark:bg-rose-500/20 text-rose-600 dark:text-rose-400"
        />
        <SummaryCard
          title="Avg Congestion Index"
          value={typeof stats.avgTci === 'number' ? stats.avgTci.toFixed(2) : '1.05'}
          subtitle="TCI (1.0 = smooth flow)"
          icon={Clock}
          colorClass="bg-emerald-100 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400"
        />
      </div>

      {/* Table Container */}
      <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-gray-50/50 dark:bg-slate-800/40">
          <h2 className="font-bold text-sm text-gray-800 dark:text-slate-200">Recent Route Inferences</h2>
          <select
            value={congestionFilter}
            onChange={(e) => {
              setCongestionFilter(e.target.value);
              setPage(1);
            }}
            className="border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3 py-1.5 text-xs text-gray-800 dark:text-slate-200 focus:ring-2 focus:ring-indigo-600 outline-none"
          >
            <option value="">All Congestion Levels</option>
            <option value="Low">Low Congestion</option>
            <option value="Moderate">Moderate Congestion</option>
            <option value="High">High Congestion</option>
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs whitespace-nowrap">
            <thead className="bg-gray-50 dark:bg-slate-800/60 border-b border-gray-200 dark:border-slate-800 text-gray-600 dark:text-slate-400">
              <tr>
                <th className="px-5 py-3 font-semibold">Prediction ID</th>
                <th className="px-5 py-3 font-semibold">User</th>
                <th className="px-5 py-3 font-semibold">Route (Origin → Destination)</th>
                <th className="px-5 py-3 font-semibold">Timestamp</th>
                <th className="px-5 py-3 font-semibold">Predicted TCI</th>
                <th className="px-5 py-3 font-semibold">Congestion</th>
                <th className="px-5 py-3 font-semibold">Model Version</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-slate-800/50">
              {predictions.map((pred, i) => {
                const src = pred.source || pred.source_label || 'Origin';
                const dst = pred.destination || pred.destination_label || 'Destination';
                const routeText = `${src} → ${dst}`;
                const tciVal = typeof pred.predicted_tci === 'number' ? pred.predicted_tci.toFixed(2) : '1.00';
                const dateStr = pred.timestamp || (pred.created_at ? new Date(pred.created_at).toLocaleString() : '—');

                return (
                  <tr key={pred._id || i} className="hover:bg-gray-50/50 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="px-5 py-3.5 font-mono text-[11px] text-gray-500 dark:text-slate-400">
                      {(pred._id || '').substring(0, 8)}...
                    </td>
                    <td className="px-5 py-3.5 font-medium text-gray-700 dark:text-slate-300">
                      {pred.user || 'Public User'}
                    </td>
                    <td className="px-5 py-3.5 font-medium text-gray-900 dark:text-slate-100 max-w-xs truncate" title={routeText}>
                      <span className="text-indigo-600 dark:text-indigo-400">{src}</span>
                      <span className="text-gray-400 mx-1.5">→</span>
                      <span className="text-emerald-600 dark:text-emerald-400">{dst}</span>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-gray-500 dark:text-slate-400">
                      {dateStr}
                    </td>
                    <td className="px-5 py-3.5 font-mono font-bold text-gray-800 dark:text-slate-200">
                      {tciVal}
                    </td>
                    <td className="px-5 py-3.5">
                      <CongestionBadge level={pred.congestion_level} />
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/40">
                        {pred.model_version || 'PatchTST_v2'}
                      </span>
                    </td>
                  </tr>
                );
              })}
              {predictions.length === 0 && !loading && (
                <tr>
                  <td colSpan="7" className="px-6 py-8 text-center text-gray-400 dark:text-slate-500 text-xs">
                    No predictions recorded yet. Plan a route on the user platform to see entries.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="p-4 border-t border-gray-200 dark:border-slate-800 flex justify-between items-center text-xs text-gray-600 dark:text-slate-400 bg-gray-50/50 dark:bg-slate-800/40">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3.5 py-1.5 border border-gray-300 dark:border-slate-700 rounded-lg hover:bg-white dark:hover:bg-slate-800 bg-white dark:bg-slate-900 disabled:opacity-50 transition-colors"
          >
            Previous
          </button>
          <span>Page {page} of {totalPages}</span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={page >= totalPages || predictions.length < 25}
            className="px-3.5 py-1.5 border border-gray-300 dark:border-slate-700 rounded-lg hover:bg-white dark:hover:bg-slate-800 bg-white dark:bg-slate-900 disabled:opacity-50 transition-colors"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
