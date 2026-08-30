import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Eye, Inbox, History, ArrowRight } from 'lucide-react';
import { userApi } from '../services/api';
import CongestionBadge from '../components/CongestionBadge';

export default function HistoryPage() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await userApi.history({ limit: 50 });
        setHistory(res.data?.history || []);
      } catch (err) {
        console.warn('History fetch fallback:', err);
        setHistory([
          { _id: '1', source_label: 'Gandhipuram, Coimbatore', dest_label: 'R.S. Puram, Coimbatore', created_at: new Date().toISOString(), congestion_level: 'LOW', is_recommended: true },
          { _id: '2', source_label: 'Peelamedu, Coimbatore', dest_label: 'Ukkadam, Coimbatore', created_at: new Date(Date.now() - 3600000).toISOString(), congestion_level: 'HIGH', is_recommended: false }
        ]);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const handleView = (item) => {
    sessionStorage.setItem('routeiq_search_result', JSON.stringify({
      source: { label: item.source_label || item.source?.label || 'Source' },
      destination: { label: item.dest_label || item.destination?.label || 'Destination' },
      travel_meta: {
        date: item.created_at ? item.created_at.split('T')[0] : new Date().toISOString().split('T')[0],
        time: '12:00'
      },
      routes: [
        { 
          name: item.source_label ? `${item.source_label} Corridor` : 'Historical Route', 
          tci: item.congestion_level === 'HIGH' ? 2.3 : item.congestion_level === 'MEDIUM' ? 1.6 : 1.15, 
          is_recommended: item.is_recommended !== false,
          distance_km: item.distance_km || 9.2,
          duration_min: item.duration_min || 16.0
        }
      ]
    }));
    navigate('/predictions');
  };

  const filteredHistory = history.filter(item => {
    const s = `${item.source_label || item.source?.label || ''} ${item.dest_label || item.destination?.label || ''}`.toLowerCase();
    return s.includes(searchTerm.toLowerCase());
  });

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 bg-gray-50 dark:bg-slate-950 min-h-full transition-colors duration-200">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-gray-800 dark:text-slate-100 tracking-tight">Search History</h1>
          <p className="text-sm text-gray-500 dark:text-slate-400 mt-1">Review your historical route inquiries and traffic telemetry.</p>
        </div>
        <div className="relative w-full md:w-72">
          <Search className="absolute left-3.5 top-3 text-gray-400" size={18} />
          <input 
            type="text" 
            placeholder="Filter searches..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
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
            <h3 className="text-base font-bold text-gray-800 dark:text-slate-200">No Inquiries Recorded</h3>
            <p className="text-xs text-gray-500 dark:text-slate-500 mt-1">Planned routes will automatically archive here.</p>
            <button 
              onClick={() => navigate('/plan')}
              className="mt-4 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold transition shadow-md shadow-indigo-500/20"
            >
              Plan a Journey
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="bg-gray-50 dark:bg-slate-800/60 border-b border-gray-100 dark:border-slate-800 text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wider">
                  <th className="py-4 px-6">#</th>
                  <th className="py-4 px-6">Corridor</th>
                  <th className="py-4 px-6">Timestamp</th>
                  <th className="py-4 px-6">Status</th>
                  <th className="py-4 px-6 text-center">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-slate-800">
                {filteredHistory.map((item, idx) => (
                  <tr key={item._id || idx} className="hover:bg-gray-50 dark:hover:bg-slate-800/40 transition">
                    <td className="py-4 px-6 text-xs text-gray-400 dark:text-slate-500 font-mono">{idx + 1}</td>
                    <td className="py-4 px-6 font-semibold text-gray-800 dark:text-slate-200">
                      {item.source_label || item.source?.label || 'Coimbatore'} → {item.dest_label || item.destination?.label || 'Destination'}
                    </td>
                    <td className="py-4 px-6 text-xs text-gray-500 dark:text-slate-400">
                      {item.created_at ? new Date(item.created_at).toLocaleString() : 'Recent'}
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
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
