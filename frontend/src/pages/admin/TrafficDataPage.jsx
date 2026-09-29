import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Search, X, Database, RefreshCw, ArrowLeft } from 'lucide-react';
import { adminApi } from '../../services/api';
import { useNavigate } from 'react-router-dom';

export default function TrafficDataPage() {
  const navigate = useNavigate();
  const [records, setRecords] = useState([]);
  const [totalRecords, setTotalRecords] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    timestamp: '',
    location: '',
    road_segment: '',
    speed: '',
    traffic_value: '',
    volume: 100
  });

  const fetchRecords = async () => {
    try {
      setLoading(true);
      const res = await adminApi.getTraffic({ page, limit: 25, location: search });
      const recs = res.data?.records || [];
      setRecords(recs);
      setTotalRecords(res.data?.total || recs.length);
      setTotalPages(res.data?.pages || 1);
    } catch (err) {
      console.error('Failed to fetch traffic records:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, [page, search]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await adminApi.updateTraffic(editingId, formData);
      } else {
        await adminApi.addTraffic(formData);
      }
      setModalOpen(false);
      fetchRecords();
    } catch (err) {
      console.error('Error saving traffic record:', err);
      alert('Failed to save record: ' + (err.message || err));
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this traffic record?')) {
      try {
        await adminApi.deleteTraffic(id);
        fetchRecords();
      } catch (err) {
        console.error('Error deleting record:', err);
        alert('Failed to delete record: ' + (err.message || err));
      }
    }
  };

  const openModal = (record = null) => {
    if (record) {
      setEditingId(record._id || record.id);
      setFormData({
        timestamp: record.timestamp ? (new Date(record.timestamp).toISOString().slice(0, 19).replace('T', ' ')) : '',
        location: record.location || `Lat ${record.lat?.toFixed(3)}, Lng ${record.lng?.toFixed(3)}`,
        road_segment: record.road_segment || record.road_id || record.segment_id || '',
        speed: record.speed ?? record.speed_kmh ?? '',
        traffic_value: record.traffic_value ?? (record.current_travel_time ? (record.current_travel_time / 60).toFixed(1) : ''),
        volume: record.volume || 100
      });
    } else {
      setEditingId(null);
      setFormData({
        timestamp: new Date().toISOString().slice(0, 19).replace('T', ' '),
        location: 'Coimbatore Arterial Hub',
        road_segment: 'seg_corridor',
        speed: '40',
        traffic_value: '1.20',
        volume: 100
      });
    }
    setModalOpen(true);
  };

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
            <h1 className="text-xl font-bold tracking-tight text-gray-900 dark:text-slate-100">Traffic Data Management</h1>
            <p className="text-xs text-gray-500 dark:text-slate-400">
              Live TomTom sensor observations and historical telemetry ({totalRecords} records stored)
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => openModal()}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-3.5 py-2 rounded-xl text-xs font-semibold shadow-sm transition-all"
          >
            <Plus className="w-4 h-4" /> Add Record
          </button>
          <button
            onClick={fetchRecords}
            disabled={loading}
            className="flex items-center gap-2 px-3.5 py-2 bg-white dark:bg-slate-900 border border-gray-300 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-800 text-gray-700 dark:text-slate-300 rounded-xl text-xs font-semibold transition-all disabled:opacity-50 shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-indigo-500' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Main Table Card */}
      <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden">
        {/* Search Bar */}
        <div className="p-4 border-b border-gray-200 dark:border-slate-800 flex items-center gap-4 bg-gray-50/50 dark:bg-slate-800/40">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search by road, segment, or location..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full pl-9 pr-4 py-1.5 text-xs bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-700 rounded-xl text-gray-800 dark:text-slate-200 focus:ring-2 focus:ring-indigo-600 outline-none"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs whitespace-nowrap">
            <thead className="bg-gray-50 dark:bg-slate-800/60 border-b border-gray-200 dark:border-slate-800 text-gray-600 dark:text-slate-400">
              <tr>
                <th className="px-5 py-3 font-semibold">Timestamp</th>
                <th className="px-5 py-3 font-semibold">Road / Segment</th>
                <th className="px-5 py-3 font-semibold">Location (Coordinates)</th>
                <th className="px-5 py-3 font-semibold">Speed</th>
                <th className="px-5 py-3 font-semibold">Free-Flow Speed</th>
                <th className="px-5 py-3 font-semibold">Travel Time</th>
                <th className="px-5 py-3 font-semibold">Data Source</th>
                <th className="px-5 py-3 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-slate-800/50">
              {records.map((row, i) => {
                const tsStr = row.timestamp ? new Date(row.timestamp).toLocaleString('en-US', { month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—';
                const roadName = row.road_id || row.road_segment || row.segment_id || 'Corridor';
                const locStr = row.location || (row.lat && row.lng ? `(${row.lat.toFixed(3)}, ${row.lng.toFixed(3)})` : 'Coimbatore');
                const speedVal = row.speed_kmh ?? row.speed;
                const ffSpeedVal = row.free_flow_speed ?? (speedVal ? Math.round(speedVal * 1.3) : '—');
                const ttVal = row.current_travel_time ? `${Math.round(row.current_travel_time)}s` : (row.traffic_value || '—');
                const srcTag = row.source || (row.data_source === 'synthetic' ? 'synthetic' : 'tomtom');

                return (
                  <tr key={row._id || i} className="hover:bg-gray-50/50 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="px-5 py-3.5 font-mono text-gray-600 dark:text-slate-400">{tsStr}</td>
                    <td className="px-5 py-3.5 font-medium text-gray-900 dark:text-slate-100 max-w-xs truncate" title={roadName}>
                      {roadName}
                    </td>
                    <td className="px-5 py-3.5 text-gray-500 dark:text-slate-400">{locStr}</td>
                    <td className="px-5 py-3.5 font-mono font-semibold text-emerald-600 dark:text-emerald-400">
                      {typeof speedVal === 'number' ? `${speedVal.toFixed(1)} km/h` : (speedVal ? `${speedVal} km/h` : '—')}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-gray-600 dark:text-slate-400">
                      {typeof ffSpeedVal === 'number' ? `${ffSpeedVal.toFixed(1)} km/h` : ffSpeedVal}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-gray-600 dark:text-slate-400">{ttVal}</td>
                    <td className="px-5 py-3.5">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold ${
                        srcTag === 'tomtom'
                          ? 'bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800/40'
                          : 'bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-800/40'
                      }`}>
                        {srcTag}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right space-x-1">
                      <button
                        onClick={() => openModal(row)}
                        className="p-1 text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-950/50 rounded-lg transition-colors"
                        title="Edit Record"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDelete(row._id || row.id)}
                        className="p-1 text-red-600 hover:bg-red-50 dark:hover:bg-red-950/50 rounded-lg transition-colors"
                        title="Delete Record"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })}
              {records.length === 0 && !loading && (
                <tr>
                  <td colSpan="8" className="px-6 py-8 text-center text-gray-400 dark:text-slate-500 text-xs">
                    No traffic records found matching filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 border-t border-gray-200 dark:border-slate-800 flex justify-between items-center text-xs text-gray-600 dark:text-slate-400 bg-gray-50/50 dark:bg-slate-800/40">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3.5 py-1.5 border border-gray-300 dark:border-slate-700 rounded-lg hover:bg-white dark:hover:bg-slate-800 bg-white dark:bg-slate-900 disabled:opacity-50 transition-colors"
          >
            Previous
          </button>
          <span>Page {page} of {totalPages} ({totalRecords} total items)</span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={page >= totalPages || records.length < 25}
            className="px-3.5 py-1.5 border border-gray-300 dark:border-slate-700 rounded-lg hover:bg-white dark:hover:bg-slate-800 bg-white dark:bg-slate-900 disabled:opacity-50 transition-colors"
          >
            Next
          </button>
        </div>
      </div>

      {/* Add/Edit Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-slate-800 flex justify-between items-center bg-gray-50/50 dark:bg-slate-800/40">
              <h2 className="text-sm font-bold text-gray-900 dark:text-slate-100">
                {editingId ? 'Edit Traffic Record' : 'Add Traffic Record'}
              </h2>
              <button onClick={() => setModalOpen(false)} className="text-gray-400 hover:text-gray-600 dark:hover:text-slate-200">
                <X className="w-4 h-4" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs">
              <div>
                <label className="block font-medium text-gray-700 dark:text-slate-300 mb-1">Timestamp</label>
                <input
                  type="text"
                  required
                  value={formData.timestamp}
                  onChange={e => setFormData({ ...formData, timestamp: e.target.value })}
                  className="w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-slate-200 rounded-xl px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-600"
                  placeholder="YYYY-MM-DD HH:mm:ss"
                />
              </div>
              <div>
                <label className="block font-medium text-gray-700 dark:text-slate-300 mb-1">Location Label</label>
                <input
                  type="text"
                  required
                  value={formData.location}
                  onChange={e => setFormData({ ...formData, location: e.target.value })}
                  className="w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-slate-200 rounded-xl px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-600"
                />
              </div>
              <div>
                <label className="block font-medium text-gray-700 dark:text-slate-300 mb-1">Road Segment / ID</label>
                <input
                  type="text"
                  required
                  value={formData.road_segment}
                  onChange={e => setFormData({ ...formData, road_segment: e.target.value })}
                  className="w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-slate-200 rounded-xl px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-600"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-medium text-gray-700 dark:text-slate-300 mb-1">Speed (km/h)</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={formData.speed}
                    onChange={e => setFormData({ ...formData, speed: e.target.value })}
                    className="w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-slate-200 rounded-xl px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-600"
                  />
                </div>
                <div>
                  <label className="block font-medium text-gray-700 dark:text-slate-300 mb-1">Travel Time (min)</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={formData.traffic_value}
                    onChange={e => setFormData({ ...formData, traffic_value: e.target.value })}
                    className="w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-slate-200 rounded-xl px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-600"
                  />
                </div>
              </div>
              <div className="pt-4 flex justify-end gap-3 border-t border-gray-200 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-4 py-2 border border-gray-300 dark:border-slate-700 rounded-xl hover:bg-gray-50 dark:hover:bg-slate-800 text-gray-700 dark:text-slate-300 font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium transition-colors shadow-sm"
                >
                  Save Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
