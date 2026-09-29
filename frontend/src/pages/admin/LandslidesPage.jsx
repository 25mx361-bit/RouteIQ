import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  AlertOctagon,
  ShieldAlert,
  Plus,
  Search,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  X,
  Play,
  Check,
  Trash2,
  MapPin,
  Clock,
  Droplets,
} from 'lucide-react';
import NotificationPanel from '../../components/NotificationPanel';

const GHAT_PRESETS = [
  {
    name: 'Coonoor Ghat NH-181 (Hairpin 7-9)',
    region: 'Mettupalayam - Coonoor Ghat Road',
    road: 'NH-181 Ghat Road',
    lat: 11.3200,
    lng: 76.8800,
    rainfall: 75.0,
  },
  {
    name: 'Valparai Hairpin Bends 20-25',
    region: 'Anamalai Tiger Reserve Corridor',
    road: 'SH-78 Pollachi-Valparai Rd',
    lat: 10.3600,
    lng: 76.9600,
    rainfall: 90.0,
  },
  {
    name: 'Kotagiri Ghat Road (Mettupalayam Link)',
    region: 'Eastern Nilgiris Foothills',
    road: 'SH-15 Kotagiri Road',
    lat: 11.3600,
    lng: 76.9100,
    rainfall: 60.0,
  },
  {
    name: 'Marudhamalai Hill Temple Pass',
    region: 'Western Coimbatore Foothills',
    road: 'Marudhamalai Temple Hill Rd',
    lat: 11.0450,
    lng: 76.8500,
    rainfall: 50.0,
  },
];

export default function LandslidesPage() {
  const navigate = useNavigate();
  const [landslides, setLandslides] = useState([]);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [alertMsg, setAlertMsg] = useState(null);

  const [formData, setFormData] = useState({
    title: '',
    status: 'ACTIVE',
    severity: 'CRITICAL',
    risk_level: 'Severe',
    region_name: 'Mettupalayam - Coonoor Ghat Road',
    road_name: 'NH-181 Hairpin 7-9',
    lat: 11.3200,
    lng: 76.8800,
    radius_m: 3000.0,
    rainfall_mm: 75.0,
    description: 'Severe boulder fall and rock debris blocking traffic lanes.',
  });

  const fetchLandslides = async () => {
    setLoading(true);
    try {
      const resp = await axios.get('/api/landslides', {
        params: { status: statusFilter === 'ALL' ? '' : statusFilter },
      });
      setLandslides(resp.data.landslides || []);
    } catch (err) {
      console.warn('Failed to load landslides:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLandslides();
  }, [statusFilter]);

  const handleActivate = async (id) => {
    try {
      await axios.put(`/api/landslides/${id}/activate`);
      setAlertMsg({ type: 'success', text: 'Hazard activated! Road blockade enforced & broadcast sent.' });
      fetchLandslides();
    } catch (err) {
      setAlertMsg({ type: 'error', text: 'Failed to activate hazard.' });
    }
  };

  const handleResolve = async (id) => {
    try {
      await axios.put(`/api/landslides/${id}/resolve`);
      setAlertMsg({ type: 'success', text: 'Hazard marked RESOLVED! Road restriction lifted.' });
      fetchLandslides();
    } catch (err) {
      setAlertMsg({ type: 'error', text: 'Failed to resolve hazard.' });
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this hazard record?')) return;
    try {
      await axios.delete(`/api/landslides/${id}`);
      setAlertMsg({ type: 'success', text: 'Landslide record deleted.' });
      fetchLandslides();
    } catch (err) {
      setAlertMsg({ type: 'error', text: 'Failed to delete record.' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/landslides', formData);
      setAlertMsg({ type: 'success', text: 'New landslide hazard entered and broadcasted!' });
      setIsModalOpen(false);
      fetchLandslides();
    } catch (err) {
      setAlertMsg({ type: 'error', text: err.response?.data?.message || 'Failed to enter hazard.' });
    }
  };

  const activeCount = landslides.filter((l) => l.is_active || l.status === 'ACTIVE').length;

  return (
    <div className="p-6 md:p-8 space-y-6 bg-gray-50 dark:bg-slate-950 text-gray-900 dark:text-slate-100 min-h-full transition-colors duration-200">
      {/* Top Banner */}
      <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-rose-600 dark:bg-rose-500 text-white flex items-center justify-center shadow-md shadow-rose-500/20">
            <AlertOctagon className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base md:text-lg font-bold text-gray-900 dark:text-slate-100">
                Landslide Hazard & Blockade Control
              </h2>
              <span className="text-[10px] uppercase font-mono px-2.5 py-0.5 bg-rose-50 dark:bg-red-950/60 text-rose-700 dark:text-red-400 border border-rose-200 dark:border-red-900/50 rounded-full font-bold">
                Emergency Console
              </span>
            </div>
            <p className="text-xs text-gray-500 dark:text-slate-400 mt-0.5">
              Admin-Entered Landslide Blockades (Real-time safety policy excludes blocked corridors)
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          <button
            onClick={() => navigate('/admin')}
            className="px-4 py-2 rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-gray-50 dark:hover:bg-slate-700 text-xs font-semibold text-gray-700 dark:text-slate-200 shadow-sm transition"
          >
            Back to Map
          </button>

          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold shadow-md shadow-rose-500/20 transition cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Report Landslide</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="space-y-6">
        {/* Alert Notification */}
        {alertMsg && (
          <div
            className={`p-3.5 rounded-2xl text-xs flex items-center justify-between shadow-sm ${
              alertMsg.type === 'success'
                ? 'bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300'
                : 'bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-300'
            }`}
          >
            <span>{alertMsg.text}</span>
            <button onClick={() => setAlertMsg(null)}>
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 shadow-sm flex items-center gap-3.5">
            <div className="p-3 bg-rose-50 dark:bg-red-500/10 text-rose-600 dark:text-red-400 rounded-xl border border-rose-200 dark:border-red-500/20">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[10px] text-gray-500 dark:text-slate-400 uppercase font-bold tracking-wider">Active Hazard Blockades</div>
              <div className="text-xl font-black text-rose-600 dark:text-red-400">{activeCount} Corridors Closed</div>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 shadow-sm flex items-center gap-3.5">
            <div className="p-3 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-xl border border-emerald-200 dark:border-emerald-500/20">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[10px] text-gray-500 dark:text-slate-400 uppercase font-bold tracking-wider">Resolved Restorations</div>
              <div className="text-xl font-black text-emerald-600 dark:text-emerald-400">
                {landslides.filter((l) => l.status === 'RESOLVED').length} Restored
              </div>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 shadow-sm flex items-center gap-3.5">
            <div className="p-3 bg-indigo-50 dark:bg-blue-500/10 text-indigo-600 dark:text-blue-400 rounded-xl border border-indigo-200 dark:border-blue-500/20">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[10px] text-gray-500 dark:text-slate-400 uppercase font-bold tracking-wider">Safety Policy</div>
              <div className="text-xs font-semibold text-gray-800 dark:text-slate-200">Blocked routes NEVER recommended</div>
            </div>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="flex items-center justify-between bg-white dark:bg-slate-900 p-4 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center gap-1.5">
            {['ALL', 'ACTIVE', 'RESOLVED'].map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                  statusFilter === status
                    ? 'bg-rose-600 text-white shadow-sm font-bold'
                    : 'bg-gray-100 dark:bg-slate-800 text-gray-600 dark:text-slate-400 hover:bg-gray-200 dark:hover:bg-slate-700'
                }`}
              >
                {status} HAZARDS
              </button>
            ))}
          </div>

          {loading && (
            <div className="flex items-center gap-1.5 text-xs text-rose-600 dark:text-red-400 animate-pulse font-semibold">
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Syncing hazards...</span>
            </div>
          )}
        </div>

        {/* Landslides List or Clean Reassuring Empty State */}
        {landslides.length === 0 && !loading ? (
          <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-3xl p-12 text-center shadow-sm space-y-3">
            <div className="w-14 h-14 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto border border-emerald-200 dark:border-emerald-800/80 shadow-md">
              <CheckCircle2 className="w-7 h-7" />
            </div>
            <h3 className="text-base font-bold text-gray-900 dark:text-slate-100">
              All Corridors & Ghat Roads Passable
            </h3>
            <p className="text-xs text-gray-500 dark:text-slate-400 max-w-md mx-auto leading-relaxed">
              No active landslide hazards or rockfall blockades currently reported across Coimbatore, Nilgiris, or Valparai ghat corridors.
            </p>
            <div className="pt-2">
              <button
                onClick={() => setIsModalOpen(true)}
                className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold shadow-md shadow-rose-500/20 transition"
              >
                <Plus className="w-4 h-4" />
                <span>Report Emergency Hazard</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {landslides.map((ls) => {
              const isActive = ls.is_active || ls.status === 'ACTIVE';
              return (
                <div
                  key={ls._id}
                  className={`p-5 rounded-2xl border transition-all space-y-3 shadow-sm ${
                    isActive
                      ? 'bg-rose-50/70 dark:bg-red-950/20 border-rose-300 dark:border-red-500/50 shadow-md'
                      : 'bg-white dark:bg-slate-900/60 border-gray-200 dark:border-slate-800'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span
                          className={`w-2.5 h-2.5 rounded-full ${
                            isActive ? 'bg-rose-500 animate-ping' : 'bg-emerald-500'
                          }`}
                        ></span>
                        <h4 className="text-sm font-bold text-gray-900 dark:text-slate-100">{ls.title}</h4>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">{ls.description}</p>
                    </div>

                    <span
                      className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border uppercase shrink-0 ${
                        isActive
                          ? 'bg-rose-100 dark:bg-red-500/20 text-rose-700 dark:text-red-300 border-rose-200 dark:border-red-500/50'
                          : 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-500/30'
                      }`}
                    >
                      {ls.status || (isActive ? 'ACTIVE' : 'RESOLVED')}
                    </span>
                  </div>

                  {/* Location & Radius Details */}
                  <div className="grid grid-cols-2 gap-2 text-xs bg-gray-50 dark:bg-slate-950/80 p-3 rounded-xl border border-gray-100 dark:border-slate-800">
                    <div className="flex items-center gap-1.5 text-gray-700 dark:text-slate-300">
                      <MapPin className="w-3.5 h-3.5 text-rose-500 shrink-0" />
                      <span className="truncate">{ls.region_name}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-gray-700 dark:text-slate-300">
                      <ShieldAlert className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                      <span className="truncate">{ls.road_name}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-gray-500 dark:text-slate-400 pt-1">
                    <div className="flex items-center gap-1">
                      <Droplets className="w-3.5 h-3.5 text-sky-500" />
                      <span>Rainfall: {ls.rainfall_mm || 0}mm · Radius: {ls.radius_m}m</span>
                    </div>

                    <div className="flex items-center gap-2">
                      {isActive ? (
                        <button
                          onClick={() => handleResolve(ls._id)}
                          className="flex items-center gap-1 px-3 py-1 bg-emerald-50 dark:bg-emerald-500/10 hover:bg-emerald-100 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-500/30 rounded-xl font-semibold transition"
                        >
                          <Check className="w-3 h-3" />
                          <span>Mark Resolved</span>
                        </button>
                      ) : (
                        <button
                          onClick={() => handleActivate(ls._id)}
                          className="flex items-center gap-1 px-3 py-1 bg-rose-50 dark:bg-red-500/10 hover:bg-rose-100 text-rose-700 dark:text-red-300 border border-rose-200 dark:border-red-500/30 rounded-xl font-semibold transition"
                        >
                          <Play className="w-3 h-3" />
                          <span>Re-Activate</span>
                        </button>
                      )}

                      <button
                        onClick={() => handleDelete(ls._id)}
                        className="p-1.5 text-gray-400 hover:text-rose-600 transition"
                        title="Delete record"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Add Landslide Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-3xl shadow-2xl w-full max-w-xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="px-6 py-4 border-b border-gray-100 dark:border-slate-800 flex items-center justify-between bg-gray-50/70 dark:bg-slate-950/60">
              <h3 className="text-sm font-bold text-gray-900 dark:text-slate-100 flex items-center gap-2">
                <AlertOctagon className="w-4 h-4 text-rose-600 dark:text-red-400" />
                Report Emergency Landslide Hazard
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-gray-400 hover:text-gray-600 dark:hover:text-slate-200">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4 overflow-y-auto flex-1 text-xs">
              <div>
                <label className="block text-gray-700 dark:text-slate-300 font-semibold mb-1">Hazard Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Severe Rockfall at Hairpin 8"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full bg-gray-50 dark:bg-slate-950 border border-gray-200 dark:border-slate-800 px-3.5 py-2.5 rounded-xl text-gray-900 dark:text-slate-100 focus:outline-none focus:border-rose-500 transition"
                />
              </div>

              {/* Ghat Road Presets */}
              <div className="space-y-1.5">
                <label className="block text-gray-700 dark:text-slate-300 font-semibold">Quick Ghat Corridor Presets</label>
                <div className="flex flex-wrap gap-1.5">
                  {GHAT_PRESETS.map((gp) => (
                    <button
                      key={gp.name}
                      type="button"
                      onClick={() =>
                        setFormData({
                          ...formData,
                          title: `Rockfall Hazard at ${gp.name}`,
                          region_name: gp.region,
                          road_name: gp.road,
                          lat: gp.lat,
                          lng: gp.lng,
                          rainfall_mm: gp.rainfall,
                        })
                      }
                      className="px-2.5 py-1 rounded-lg bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 dark:hover:bg-slate-700 text-[10px] text-gray-700 dark:text-slate-300 border border-gray-200 dark:border-slate-700 transition"
                    >
                      {gp.name}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-gray-700 dark:text-slate-300 font-semibold mb-1">Region Name</label>
                  <input
                    type="text"
                    value={formData.region_name}
                    onChange={(e) => setFormData({ ...formData, region_name: e.target.value })}
                    className="w-full bg-gray-50 dark:bg-slate-950 border border-gray-200 dark:border-slate-800 px-3.5 py-2.5 rounded-xl text-gray-900 dark:text-slate-100 focus:outline-none focus:border-rose-500 transition"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 dark:text-slate-300 font-semibold mb-1">Road / Highway Name</label>
                  <input
                    type="text"
                    value={formData.road_name}
                    onChange={(e) => setFormData({ ...formData, road_name: e.target.value })}
                    className="w-full bg-gray-50 dark:bg-slate-950 border border-gray-200 dark:border-slate-800 px-3.5 py-2.5 rounded-xl text-gray-900 dark:text-slate-100 focus:outline-none focus:border-rose-500 transition"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-gray-700 dark:text-slate-300 font-semibold mb-1">Latitude</label>
                  <input
                    type="number"
                    step="any"
                    value={formData.lat}
                    onChange={(e) => setFormData({ ...formData, lat: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-gray-50 dark:bg-slate-950 border border-gray-200 dark:border-slate-800 px-3.5 py-2.5 rounded-xl text-gray-900 dark:text-slate-100 font-mono focus:outline-none focus:border-rose-500 transition"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 dark:text-slate-300 font-semibold mb-1">Longitude</label>
                  <input
                    type="number"
                    step="any"
                    value={formData.lng}
                    onChange={(e) => setFormData({ ...formData, lng: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-gray-50 dark:bg-slate-950 border border-gray-200 dark:border-slate-800 px-3.5 py-2.5 rounded-xl text-gray-900 dark:text-slate-100 font-mono focus:outline-none focus:border-rose-500 transition"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-gray-700 dark:text-slate-300 font-semibold mb-1">Blockage Radius (meters)</label>
                  <input
                    type="number"
                    value={formData.radius_m}
                    onChange={(e) => setFormData({ ...formData, radius_m: parseFloat(e.target.value) || 2500 })}
                    className="w-full bg-gray-50 dark:bg-slate-950 border border-gray-200 dark:border-slate-800 px-3.5 py-2.5 rounded-xl text-gray-900 dark:text-slate-100 focus:outline-none focus:border-rose-500 transition"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 dark:text-slate-300 font-semibold mb-1">Rainfall (mm)</label>
                  <input
                    type="number"
                    value={formData.rainfall_mm}
                    onChange={(e) => setFormData({ ...formData, rainfall_mm: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-gray-50 dark:bg-slate-950 border border-gray-200 dark:border-slate-800 px-3.5 py-2.5 rounded-xl text-gray-900 dark:text-slate-100 focus:outline-none focus:border-rose-500 transition"
                  />
                </div>
              </div>

              <div>
                <label className="block text-gray-700 dark:text-slate-300 font-semibold mb-1">Description & Debris Details</label>
                <textarea
                  rows={2}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full bg-gray-50 dark:bg-slate-950 border border-gray-200 dark:border-slate-800 px-3.5 py-2.5 rounded-xl text-gray-900 dark:text-slate-100 focus:outline-none focus:border-rose-500 transition"
                ></textarea>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2.5 rounded-xl border border-gray-200 dark:border-slate-700 bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 dark:hover:bg-slate-700 text-gray-700 dark:text-slate-300 font-semibold transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold shadow-md shadow-rose-500/20 transition"
                >
                  Enter Hazard & Block Route
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
