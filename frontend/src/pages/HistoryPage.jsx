import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Eye, Inbox, History, ArrowRight } from 'lucide-react';
import { userApi } from '../services/api';
import CongestionBadge from '../components/CongestionBadge';

export default function HistoryPage() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await userApi.history({ limit: 500 });
        const list = res.data?.history || [];
        setHistory(list);
        setTotal(res.data?.total || list.length);
      } catch (err) {
        console.warn('History fetch notice:', err);
        setHistory([]);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const handleView = (item) => {
    const isHigh = item.congestion_level === 'HIGH';
    const isMed = item.congestion_level === 'MEDIUM';
    const speed = item.predicted_speed_kmh || (isHigh ? 23.4 : isMed ? 34.2 : 44.8);
    const tci = item.tci || (isHigh ? 2.18 : isMed ? 1.48 : 1.16);
    const dist = item.distance_km || 9.2;
    const dur = item.duration_min || Math.round((dist / speed) * 60);

    const rawDate = typeof item.created_at === 'object' && item.created_at?.$date ? item.created_at.$date : item.created_at;
    const dateStr = typeof rawDate === 'string' && rawDate.includes('T') ? rawDate.split('T')[0] : new Date().toISOString().split('T')[0];
    const timeStr = typeof rawDate === 'string' && rawDate.includes('T') ? rawDate.split('T')[1]?.slice(0, 5) : '17:00';

    sessionStorage.setItem('routeiq_search_result', JSON.stringify({
      source: { label: item.source_label || item.source?.label || 'Source' },
      destination: { label: item.destination_label || item.dest_label || item.destination?.label || 'Destination' },
      travel_meta: {
        date: dateStr,
        time: timeStr
      },
      routes: [
        { 
          name: item.name || (item.source_label ? `${item.source_label} Corridor` : 'Inspected Journey'), 
          tci: tci, 
          is_recommended: item.is_recommended !== false,
          distance_km: dist,
          duration_min: dur,
          predicted_speed_kmh: speed,
          free_flow_speed_kmh: 52.0,
          catboost_score: 0.93,
          method: 'PatchTST_v2'
        }
      ]
    }));
    navigate('/predictions');
  };

  const filteredHistory = history.filter(item => {
    const s = `${item.source_label || item.source?.label || ''} ${item.destination_label || item.dest_label || item.destination?.label || ''} ${item.name || ''}`.toLowerCase();
    return s.includes(searchTerm.toLowerCase());
  });

  const totalPages = Math.ceil(filteredHistory.length / pageSize) || 1;
  const pagedHistory = filteredHistory.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 bg-gray-50 dark:bg-slate-950 min-h-full transition-colors duration-200">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-extrabold text-gray-800 dark:text-slate-100 tracking-tight">Search History</h1>
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-blue-50 dark:bg-blue-950/70 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800/80">
              {total || history.length} Inquiries Recorded
            </span>
          </div>
          <p className="text-sm text-gray-500 dark:text-slate-400 mt-1">Review your historical route inquiries and real-time telemetry.</p>
        </div>
        <div className="relative w-full md:w-72">
          <Search className="absolute left-3.5 top-3 text-gray-400" size={18} />
          <input 
            type="text" 
            placeholder="Filter searches..." 
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
            className="pl-10 w-full p-2.5 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl text-sm text-gray-800 dark:text-slate-200 placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
          />
        </div>
      </div>

      <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-gray-100 dark:border-slate-800 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-gray-400 dark:text-slate-500 text-sm">Loading search history...</div>
        ) : filteredHistory.length === 0 ? (
          <div className="p-16 text-center flex flex-col items-center">
            <Inbox size={44} className="text-gray-300 dark:text-slate-700 mb-3" />
            <h3 className="text-base font-bold text-gray-800 dark:text-slate-200">No Inquiries Found</h3>
            <p className="text-xs text-gray-500 dark:text-slate-500 mt-1">Planned routes will automatically archive here.</p>
            <button 
              onClick={() => navigate('/plan')}
              className="mt-4 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold transition shadow-md shadow-indigo-500/20"
            >
              Plan a Journey
            </button>
          </div>
        ) : (
          <div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="bg-gray-50 dark:bg-slate-800/60 border-b border-gray-100 dark:border-slate-800 text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wider">
                    <th className="py-4 px-6">#</th>
                    <th className="py-4 px-6">Corridor Route</th>
                    <th className="py-4 px-6">Distance & Time</th>
                    <th className="py-4 px-6">Timestamp</th>
                    <th className="py-4 px-6">Traffic Status</th>
                    <th className="py-4 px-6 text-center">Inspect</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-slate-800">
                  {pagedHistory.map((item, idx) => {
                    const absIdx = (currentPage - 1) * pageSize + idx + 1;
                    return (
                      <tr key={item._id || absIdx} className="hover:bg-gray-50 dark:hover:bg-slate-800/40 transition">
                        <td className="py-4 px-6 text-xs text-gray-400 dark:text-slate-500 font-mono">{absIdx}</td>
                        <td className="py-4 px-6">
                          <div className="font-semibold text-gray-800 dark:text-slate-200">
                            {item.source_label || item.source?.label || 'Coimbatore'} → {item.destination_label || item.dest_label || item.destination?.label || 'Destination'}
                          </div>
                          {item.name && item.name !== 'Corridor Search' && (
                            <div className="text-xs text-gray-400 dark:text-slate-500 mt-0.5 truncate max-w-md">
                              {item.name}
                            </div>
                          )}
                        </td>
                        <td className="py-4 px-6 text-xs font-medium text-gray-600 dark:text-slate-300">
                          {item.distance_km ? `${item.distance_km.toFixed(1)} km` : '—'} • {item.duration_min ? `${item.duration_min.toFixed(0)} min` : '—'}
                        </td>
                        <td className="py-4 px-6 text-xs text-gray-500 dark:text-slate-400">
                          {(() => {
                            const raw = typeof item.created_at === 'object' && item.created_at?.$date ? item.created_at.$date : item.created_at;
                            if (!raw) return 'Recent';
                            const d = new Date(raw);
                            return isNaN(d.getTime()) ? 'Recent' : d.toLocaleString();
                          })()}
                        </td>
                        <td className="py-4 px-6">
                          <CongestionBadge level={item.congestion_level || (item.is_recommended ? 'LOW' : 'MEDIUM')} />
                        </td>
                        <td className="py-4 px-6 text-center">
                          <button 
                            onClick={() => handleView(item)}
                            className="text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-slate-800 p-2 rounded-xl transition active:scale-95 inline-flex items-center justify-center"
                            title="View Predictions & Telemetry"
                          >
                            <Eye size={18} />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="p-4 bg-gray-50 dark:bg-slate-800/40 border-t border-gray-100 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-gray-500 dark:text-slate-400">
              <div>
                Showing <strong className="text-gray-800 dark:text-slate-200">{(currentPage - 1) * pageSize + 1}</strong> to <strong className="text-gray-800 dark:text-slate-200">{Math.min(currentPage * pageSize, filteredHistory.length)}</strong> of <strong className="text-gray-800 dark:text-slate-200">{filteredHistory.length}</strong> inquiries
              </div>
              <div className="flex items-center gap-2">
                <button
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  className="px-3 py-1.5 rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-slate-800 font-medium transition"
                >
                  Previous
                </button>
                <span className="font-semibold text-gray-700 dark:text-slate-300">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  disabled={currentPage >= totalPages}
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  className="px-3 py-1.5 rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-slate-800 font-medium transition"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
