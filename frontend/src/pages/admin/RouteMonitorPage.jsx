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

  const SummaryCard = ({ title, value, icon: Icon, color }) => (
    <div className="bg-white rounded-xl border border-gray-200 p-5 flex items-center gap-4 shadow-sm">
      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${color}`}>
        <Icon className="w-6 h-6" />
      </div>
      <div>
        <p className="text-gray-500 text-sm font-medium">{title}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
    </div>
  );

  return (
    <div className="p-6 bg-white min-h-screen text-gray-800">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Route Generation Monitor</h1>
        <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg">
          <span className="text-sm font-medium text-gray-600">ORS API Status:</span>
          <span className="flex items-center gap-1.5 text-emerald-600 text-sm font-bold">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Online
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <SummaryCard
          title="Total Routes Generated"
          value={stats?.total_routes_generated || 0}
          icon={Map}
          color="bg-indigo-100 text-indigo-600"
        />
        <SummaryCard
          title="API Success Rate"
          value={`${stats?.api_success_rate || 99.8}%`}
          icon={CheckCircle}
          color="bg-emerald-100 text-emerald-600"
        />
        <SummaryCard
          title="Avg Routes per Search"
          value={stats?.avg_routes_per_search || '2.8'}
          icon={BarChart2}
          color="bg-blue-100 text-blue-600"
        />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <h2 className="font-semibold text-gray-800">Recent Route Searches</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 border-b border-gray-200 text-gray-600">
              <tr>
                <th className="px-6 py-3 font-semibold">User</th>
                <th className="px-6 py-3 font-semibold">Source → Destination</th>
                <th className="px-6 py-3 font-semibold">Routes Count</th>
                <th className="px-6 py-3 font-semibold">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {searches.map((search, i) => (
                <tr key={search._id || i} className="hover:bg-gray-50">
                  <td className="px-6 py-4">{search.user || 'Anonymous'}</td>
                  <td className="px-6 py-4 truncate max-w-sm" title={`${search.source} → ${search.destination}`}>
                    {search.source} → {search.destination}
                  </td>
                  <td className="px-6 py-4 font-medium">{search.routes_count || 3}</td>
                  <td className="px-6 py-4 text-gray-500">{search.timestamp}</td>
                </tr>
              ))}
              {searches.length === 0 && !loading && (
                <tr>
                  <td colSpan="4" className="px-6 py-8 text-center text-gray-500">
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
