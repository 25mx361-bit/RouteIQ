import React, { useState, useEffect } from 'react';
import { adminApi } from '../../services/api';
import CongestionBadge from '../../components/CongestionBadge';
import { Activity, Clock, AlertTriangle } from 'lucide-react';

export default function PredictionMonitorPage() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [congestionFilter, setCongestionFilter] = useState('');
  const [stats, setStats] = useState({ total: 0, highCongestion: 0, avgTci: 0 });

  useEffect(() => {
    fetchPredictions();
  }, [page, congestionFilter]);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      const res = await adminApi.getPredictionsList({ page, limit: 50, congestion: congestionFilter });
      setPredictions(res.data?.predictions || []);
      if (res.data?.stats) {
        setStats(res.data.stats);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

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
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Prediction Monitor</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <SummaryCard
          title="Total Predictions"
          value={stats.total}
          icon={Activity}
          color="bg-indigo-100 text-indigo-600"
        />
        <SummaryCard
          title="High Congestion"
          value={stats.highCongestion}
          icon={AlertTriangle}
          color="bg-red-100 text-red-600"
        />
        <SummaryCard
          title="Avg TCI"
          value={stats.avgTci?.toFixed(2) || '0.00'}
          icon={Clock}
          color="bg-emerald-100 text-emerald-600"
        />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
          <h2 className="font-semibold text-gray-800">Recent Predictions</h2>
          <select
            value={congestionFilter}
            onChange={(e) => setCongestionFilter(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-600 outline-none"
          >
            <option value="">All Congestion Levels</option>
            <option value="Low">Low</option>
            <option value="Moderate">Moderate</option>
            <option value="High">High</option>
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 border-b border-gray-200 text-gray-600">
              <tr>
                <th className="px-6 py-3 font-semibold">Prediction ID</th>
                <th className="px-6 py-3 font-semibold">User</th>
                <th className="px-6 py-3 font-semibold">Route (Src → Dest)</th>
                <th className="px-6 py-3 font-semibold">Time</th>
                <th className="px-6 py-3 font-semibold">Predicted TCI</th>
                <th className="px-6 py-3 font-semibold">Congestion</th>
                <th className="px-6 py-3 font-semibold">Model Version</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {predictions.map((pred, i) => (
                <tr key={pred._id || i} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-mono text-xs text-gray-500">
                    {(pred._id || pred.id || '').substring(0, 8)}...
                  </td>
                  <td className="px-6 py-4">{pred.user || 'Anonymous'}</td>
                  <td className="px-6 py-4 truncate max-w-xs" title={`${pred.source} → ${pred.destination}`}>
                    {pred.source} → {pred.destination}
                  </td>
                  <td className="px-6 py-4 text-gray-500">{pred.timestamp}</td>
                  <td className="px-6 py-4 font-medium">{pred.predicted_tci?.toFixed(2)}</td>
                  <td className="px-6 py-4">
                    <CongestionBadge level={pred.congestion_level} />
                  </td>
                  <td className="px-6 py-4 text-gray-500 text-xs">{pred.model_version || 'v1.0'}</td>
                </tr>
              ))}
              {predictions.length === 0 && !loading && (
                <tr>
                  <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                    No predictions found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="p-4 border-t border-gray-200 flex justify-between items-center text-sm text-gray-600 bg-gray-50">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-white bg-white disabled:opacity-50"
          >
            Previous
          </button>
          <span>Page {page}</span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={predictions.length < 50}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-white bg-white disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
