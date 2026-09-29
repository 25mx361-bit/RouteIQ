import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Settings, RefreshCw, Filter, FileText } from 'lucide-react';
import { adminApi } from '../../services/api';

export default function LogsPage() {
  const navigate = useNavigate();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [level, setLevel] = useState('');
  const [source, setSource] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchLogs();
  }, [page, level, source]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const res = await adminApi.logs({
        page,
        limit: 50,
        level,
        source
      });
      setLogs(res.data.logs);
      setTotal(res.data.total);
    } catch (err) {
      setError(err.message || 'Failed to fetch logs');
    } finally {
      setLoading(false);
    }
  };

  const getLevelColor = (lvl) => {
    switch (lvl?.toUpperCase()) {
      case 'ERROR':
      case 'CRITICAL':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
      case 'WARNING':
        return 'text-orange-400 bg-orange-500/10 border-orange-500/30';
      case 'INFO':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/30';
      default:
        return 'text-slate-400 bg-slate-800 border-slate-700';
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 text-gray-900 dark:text-slate-100">
      <div className="flex items-center justify-between pb-4 border-b border-gray-200 dark:border-slate-800">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/admin')}
            className="p-2 rounded-xl bg-white dark:bg-slate-900 hover:bg-gray-100 dark:hover:bg-slate-800 text-gray-600 dark:text-slate-400 border border-gray-200 dark:border-slate-800 transition-colors shadow-sm"
            title="Back to Admin Dashboard"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-gray-900 dark:text-slate-100 flex items-center gap-2">
              <Settings className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              System Logs
            </h1>
            <p className="text-xs text-gray-500 dark:text-slate-400">Structured system audit and scheduler telemetry logs</p>
          </div>
        </div>
        <button
          onClick={fetchLogs}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 bg-white dark:bg-slate-900 border border-gray-300 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-800 text-gray-700 dark:text-slate-300 rounded-xl text-xs font-semibold transition-all disabled:opacity-50 shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-indigo-500' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>
        {/* Filters */}
        <div className="flex flex-wrap items-center gap-4 mb-4 shrink-0 bg-white dark:bg-slate-900 p-4 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-slate-400 font-semibold mr-2">
            <Filter className="w-4 h-4" /> Filters
          </div>

          <select
            value={level}
            onChange={e => setLevel(e.target.value)}
            className="bg-gray-50 dark:bg-slate-950 border border-gray-200 dark:border-slate-700 text-gray-800 dark:text-slate-200 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-2 outline-none transition"
          >
            <option value="">All Levels</option>
            <option value="INFO">INFO</option>
            <option value="WARNING">WARNING</option>
            <option value="ERROR">ERROR</option>
          </select>

          <input
            type="text"
            placeholder="Search source (e.g. scheduler)"
            value={source}
            onChange={e => setSource(e.target.value)}
            className="bg-gray-50 dark:bg-slate-950 border border-gray-200 dark:border-slate-700 text-gray-800 dark:text-slate-200 text-sm rounded-xl focus:ring-indigo-500 focus:border-indigo-500 block p-2 outline-none min-w-[200px] transition"
          />

          <div className="ml-auto text-sm text-gray-500 dark:text-slate-400 font-mono">
            Showing {logs.length} of {total}
          </div>
        </div>

        {error && <div className="text-rose-500 dark:text-rose-400 text-sm p-4 mb-4 bg-rose-500/10 rounded-xl shrink-0">{error}</div>}

        {/* Log Table */}
        <div className="flex-1 overflow-auto bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-2xl shadow-sm relative">
          <table className="w-full text-left text-sm relative">
            <thead className="bg-gray-50 dark:bg-slate-800/80 backdrop-blur border-b border-gray-200 dark:border-slate-700 text-gray-600 dark:text-slate-400 sticky top-0">
              <tr>
                <th className="px-4 py-3 font-semibold w-40">Timestamp</th>
                <th className="px-4 py-3 font-semibold w-24">Level</th>
                <th className="px-4 py-3 font-semibold w-48">Source</th>
                <th className="px-4 py-3 font-semibold">Message</th>
                <th className="px-4 py-3 font-semibold w-32">User ID</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-slate-800 font-mono text-[11px]">
              {logs.map(log => (
                <tr key={log._id} className="hover:bg-gray-50/50 dark:hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-2 text-gray-500 dark:text-slate-400">
                    {new Date(log.logged_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-0.5 rounded border ${getLevelColor(log.level)}`}>
                      {log.level}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-gray-700 dark:text-slate-300 truncate max-w-[12rem]" title={log.source}>
                    {log.source}
                  </td>
                  <td className="px-4 py-2 text-gray-800 dark:text-slate-300">
                    <div className="break-words max-w-[30rem]">{log.message}</div>
                  </td>
                  <td className="px-4 py-2 text-gray-400 dark:text-slate-500 truncate max-w-[8rem]">
                    {log.user_id || '-'}
                  </td>
                </tr>
              ))}
              {logs.length === 0 && !loading && (
                <tr>
                  <td colSpan="5" className="text-center py-12 text-gray-400 dark:text-slate-500">
                    <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    No logs found matching filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="mt-4 flex justify-between items-center shrink-0">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 rounded-xl bg-white dark:bg-slate-900 border border-gray-300 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-800 text-gray-700 dark:text-slate-200 disabled:opacity-50 text-xs font-semibold shadow-sm transition-all"
          >
            Previous
          </button>
          <span className="text-gray-500 dark:text-slate-400 text-xs font-mono">Page {page}</span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={logs.length < 50}
            className="px-4 py-2 rounded-xl bg-white dark:bg-slate-900 border border-gray-300 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-800 text-gray-700 dark:text-slate-200 disabled:opacity-50 text-xs font-semibold shadow-sm transition-all"
          >
            Next
          </button>
        </div>
      </div>
  );
}
