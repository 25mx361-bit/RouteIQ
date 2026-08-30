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
    <div className="flex flex-col h-screen w-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Top Header */}
      <header className="h-16 shrink-0 bg-slate-900/80 backdrop-blur border-b border-slate-800 px-6 flex items-center justify-between z-20">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-red-600 to-rose-500 flex items-center justify-center shadow-lg shadow-red-900/40">
            <AlertOctagon className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold tracking-tight text-white">
                Landslide Hazard & Blockade Control
              </h1>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 bg-red-500/10 text-red-400 border border-red-500/30 rounded-full">
                Admin Emergency Console
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Admin-Entered Landslide Blockades (PatchTST does NOT detect landslides)
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/admin')}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 transition-colors"
            >
              Back to Map
            </button>

          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white text-xs font-semibold shadow-lg shadow-red-900/30 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            Report Landslide
          </button>

          <NotificationPanel />
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex flex-col p-6 overflow-y-auto space-y-5">
        {/* Alert Notification */}
        {alertMsg && (
          <div
            className={`p-3 rounded-lg text-xs flex items-center justify-between ${
              alertMsg.type === 'success'
                ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-300'
                : 'bg-rose-500/10 border border-rose-500/30 text-rose-300'
            }`}
          >
            <span>{alertMsg.text}</span>
            <button onClick={() => setAlertMsg(null)}>
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-3">
            <div className="p-2 bg-red-500/10 text-red-400 rounded-lg">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400 uppercase font-medium">Active Hazard Blockades</div>
              <div className="text-lg font-black text-red-400">{activeCount} Corridors Closed</div>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-3">
            <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400 uppercase font-medium">Resolved Restorations</div>
              <div className="text-lg font-black text-emerald-400">
                {landslides.filter((l) => l.status === 'RESOLVED').length} Restored
              </div>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-3">
            <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[11px] text-slate-400 uppercase font-medium">Safety Policy</div>
              <div className="text-xs font-semibold text-slate-200">Blocked routes NEVER recommended</div>
            </div>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="flex items-center justify-between bg-slate-900/60 p-3 rounded-xl border border-slate-800">
          <div className="flex items-center gap-1.5">
            {['ALL', 'ACTIVE', 'RESOLVED'].map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                  statusFilter === status
                    ? 'bg-red-600 text-white shadow-md'
                    : 'bg-slate-800/80 text-slate-400 hover:text-slate-200'
                }`}
              >
                {status} HAZARDS
              </button>
            ))}
          </div>

          {loading && (
            <div className="flex items-center gap-1 text-xs text-red-400 animate-pulse">
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              Syncing hazards...
            </div>
          )}
        </div>

        {/* Landslides List */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {landslides.map((ls) => {
            const isActive = ls.is_active || ls.status === 'ACTIVE';
            return (
              <div
                key={ls._id}
                className={`p-4 rounded-xl border transition-all space-y-3 ${
                  isActive
                    ? 'bg-red-950/20 border-red-500/50 shadow-lg shadow-red-950/30'
                    : 'bg-slate-900/60 border-slate-800'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`w-2.5 h-2.5 rounded-full ${
                          isActive ? 'bg-red-500 animate-ping' : 'bg-emerald-400'
                        }`}
                      ></span>
                      <h4 className="text-sm font-bold text-slate-100">{ls.title}</h4>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{ls.description}</p>
                  </div>

                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase shrink-0 ${
                      isActive
                        ? 'bg-red-500/20 text-red-300 border-red-500/50'
                        : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                    }`}
                  >
                    {ls.status || (isActive ? 'ACTIVE' : 'RESOLVED')}
                  </span>
                </div>

                {/* Location & Radius Details */}
                <div className="grid grid-cols-2 gap-2 text-xs bg-slate-950/80 p-2.5 rounded-lg border border-slate-800">
                  <div className="flex items-center gap-1.5 text-slate-300">
                    <MapPin className="w-3.5 h-3.5 text-red-400 shrink-0" />
                    <span className="truncate">{ls.region_name}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-300">
                    <ShieldAlert className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    <span className="truncate">{ls.road_name}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                  <div className="flex items-center gap-1">
                    <Droplets className="w-3 h-3 text-sky-400" />
                    <span>Rainfall: {ls.rainfall_mm || 0}mm · Radius: {ls.radius_m}m</span>
                  </div>

                  <div className="flex items-center gap-2">
                    {isActive ? (
                      <button
                        onClick={() => handleResolve(ls._id)}
                        className="flex items-center gap-1 px-2.5 py-1 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded font-semibold transition-colors"
                      >
                        <Check className="w-3 h-3" />
                        Mark Resolved
                      </button>
                    ) : (
                      <button
                        onClick={() => handleActivate(ls._id)}
                        className="flex items-center gap-1 px-2.5 py-1 bg-red-500/10 hover:bg-red-500/20 text-red-300 border border-red-500/30 rounded font-semibold transition-colors"
                      >
                        <Play className="w-3 h-3" />
                        Re-Activate
                      </button>
                    )}

                    <button
                      onClick={() => handleDelete(ls._id)}
                      className="p-1 text-slate-500 hover:text-rose-400 transition-colors"
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
      </div>

      {/* Add Landslide Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl w-full max-w-xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <AlertOctagon className="w-4 h-4 text-red-400" />
                Report Emergency Landslide Hazard
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4 overflow-y-auto flex-1 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Hazard Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Severe Rockfall at Hairpin 8"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-red-500"
                />
              </div>

              {/* Ghat Road Presets */}
              <div className="space-y-1.5">
                <label className="block text-slate-400 font-medium">Quick Ghat Corridor Presets</label>
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
                      className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[10px] text-slate-300 border border-slate-700 transition-colors"
                    >
                      {gp.name}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Region Name</label>
                  <input
                    type="text"
                    value={formData.region_name}
                    onChange={(e) => setFormData({ ...formData, region_name: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-red-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Road / Highway Name</label>
                  <input
                    type="text"
                    value={formData.road_name}
                    onChange={(e) => setFormData({ ...formData, road_name: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-red-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Latitude</label>
                  <input
                    type="number"
                    step="any"
                    value={formData.lat}
                    onChange={(e) => setFormData({ ...formData, lat: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 font-mono focus:outline-none focus:border-red-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Longitude</label>
                  <input
                    type="number"
                    step="any"
                    value={formData.lng}
                    onChange={(e) => setFormData({ ...formData, lng: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 font-mono focus:outline-none focus:border-red-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Blockage Radius (meters)</label>
                  <input
                    type="number"
                    value={formData.radius_m}
                    onChange={(e) => setFormData({ ...formData, radius_m: parseFloat(e.target.value) || 2500 })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-red-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Rainfall (mm)</label>
                  <input
                    type="number"
                    value={formData.rainfall_mm}
                    onChange={(e) => setFormData({ ...formData, rainfall_mm: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-red-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Description & Debris Details</label>
                <textarea
                  rows={2}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-red-500"
                ></textarea>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white font-semibold shadow-lg shadow-red-900/30"
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
