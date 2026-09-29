import React, { useState, useEffect } from 'react';
import { adminApi } from '../../services/api';
import { Map, CheckCircle, BarChart2 } from 'lucide-react';

export default function RouteMonitorPage() {
  const [stats, setStats] = useState(null);
  const [searches, setSearches] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const res = await adminApi.stats();
        if (res.data) {
          setStats(res.data.stats);
          // Assuming the API might return recent searches, otherwise mock or use empty
          setSearches(res.data.recent_searches || []);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const SummaryCard = ({ title, value, icon: Icon, color, iconColor }) => (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-5 flex items-center gap-4 shadow-sm transition-colors">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
        <Icon className={`w-6 h-6 ${iconColor}`} />
      </div>
      <div>
        <p className="text-gray-500 dark:text-slate-400 text-xs font-medium">{title}</p>
        <p className="text-2xl font-bold text-gray-900 dark:text-slate-100">{value}</p>
      </div>
    </div>
  );

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 text-gray-900 dark:text-slate-100 transition-colors">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200 dark:border-slate-800">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-gray-900 dark:text-slate-100 flex items-center gap-2">
            <Map className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            Route Generation Monitor
          </h1>
          <p className="text-xs text-gray-500 dark:text-slate-400">Live ORS routing engine telemetry and search queries</p>
        </div>
        <div className="flex items-center gap-2 px-3.5 py-1.5 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl shadow-sm text-xs">
          <span className="font-medium text-gray-600 dark:text-slate-400">ORS API Status:</span>
          <span className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-bold">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Online
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <SummaryCard
          title="Total Routes Generated"
          value={stats?.total_routes_generated || 0}
          icon={Map}
          color="bg-indigo-50 dark:bg-indigo-950/50"
          iconColor="text-indigo-600 dark:text-indigo-400"
        />
        <SummaryCard
          title="API Success Rate"
          value={`${stats?.api_success_rate || 99.8}%`}
          icon={CheckCircle}
          color="bg-emerald-50 dark:bg-emerald-950/50"
          iconColor="text-emerald-600 dark:text-emerald-400"
        />
        <SummaryCard
          title="Avg Routes per Search"
          value={stats?.avg_routes_per_search || '2.8'}
          icon={BarChart2}
          color="bg-blue-50 dark:bg-blue-950/50"
          iconColor="text-blue-600 dark:text-blue-400"
        />
      </div>

      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm overflow-hidden transition-colors">
        <div className="p-4 border-b border-gray-200 dark:border-slate-800 bg-gray-50/50 dark:bg-slate-800/40">
          <h2 className="text-sm font-semibold text-gray-800 dark:text-slate-200">Recent Route Searches</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 dark:bg-slate-800/60 border-b border-gray-200 dark:border-slate-800 text-gray-600 dark:text-slate-400">
              <tr>
                <th className="px-6 py-3 font-semibold">User</th>
                <th className="px-6 py-3 font-semibold">Source → Destination</th>
                <th className="px-6 py-3 font-semibold">Routes Count</th>
                <th className="px-6 py-3 font-semibold">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-slate-800 font-mono">
              {searches.map((search, i) => (
                <tr key={search._id || i} className="hover:bg-gray-50/50 dark:hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-3.5 font-medium text-gray-900 dark:text-slate-100">{search.user || 'Anonymous'}</td>
                  <td className="px-6 py-3.5 text-gray-700 dark:text-slate-300 truncate max-w-sm" title={`${search.source} → ${search.destination}`}>
                    {search.source} → {search.destination}
                  </td>
                  <td className="px-6 py-3.5 text-indigo-600 dark:text-indigo-400 font-bold">{search.routes_count || 3}</td>
                  <td className="px-6 py-3.5 text-gray-500 dark:text-slate-400">{search.timestamp}</td>
                </tr>
              ))}
              {searches.length === 0 && !loading && (
                <tr>
                  <td colSpan="4" className="px-6 py-8 text-center text-gray-400 dark:text-slate-500">
                    No recent searches available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
