import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Calendar,
  Plus,
  Search,
  Filter,
  Flame,
  Heart,
  Trophy,
  Users,
  MapPin,
  Clock,
  AlertTriangle,
  RefreshCw,
  X,
  CheckCircle2,
  Trash2,
  Edit2,
  Shield,
} from 'lucide-react';
import EventCard from '../../components/EventCard';
import FestivalCard from '../../components/FestivalCard';
import MarriageEventCard from '../../components/MarriageEventCard';

const EVENT_TYPES = [
  { value: 'FESTIVAL', label: 'Festival & Temple Procession' },
  { value: 'MARRIAGE', label: 'Marriage & Reception' },
  { value: 'SPORTS_EVENT', label: 'Sports & Marathon' },
  { value: 'POLITICAL_EVENT', label: 'Political Rally / VIP' },
  { value: 'COLLEGE_EVENT', label: 'College Symposium' },
  { value: 'SCHOOL_EVENT', label: 'School Function' },
  { value: 'PUBLIC_EVENT', label: 'Public Gathering' },
  { value: 'OTHER', label: 'Other Road Event' },
];

const IMPACT_LEVELS = [
  { value: 'LOW', label: 'Low Impact (Small delays)' },
  { value: 'MEDIUM', label: 'Medium Impact (Moderate delays)' },
  { value: 'HIGH', label: 'High Impact (Heavy slowdowns)' },
  { value: 'CRITICAL', label: 'Critical Bottleneck (Road closure/choke)' },
];

const COIMBATORE_LANDMARKS = [
  { name: 'Town Hall (Raja St)', lat: 10.9950, lng: 76.9600 },
  { name: 'Codissia Fair Grounds', lat: 11.0350, lng: 77.0300 },
  { name: 'Gandhipuram Central', lat: 11.0168, lng: 76.9558 },
  { name: 'RS Puram DB Road', lat: 11.0094, lng: 76.9458 },
  { name: 'Ukkadam Bus Stand', lat: 10.9892, lng: 76.9613 },
  { name: 'PSG Tech Peelamedu', lat: 11.0244, lng: 77.0028 },
];

export default function EventsPage() {
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingEventId, setEditingEventId] = useState(null);
  const [alertMsg, setAlertMsg] = useState(null);

  // Form State
  const [formData, setFormData] = useState({
    title: '',
    event_type: 'FESTIVAL',
    description: '',
    venue_name: '',
    road_name: '',
    lat: 11.0168,
    lng: 76.9558,
    expected_crowd: 3000,
    impact_level: 'HIGH',
    start_time: new Date().toISOString().slice(0, 16),
    end_time: new Date(Date.now() + 6 * 3600 * 1000).toISOString().slice(0, 16),
  });

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const typeParam = activeTab === 'ALL' ? '' : activeTab;
      const resp = await axios.get('/api/events', {
        params: { type: typeParam },
      });
      setEvents(resp.data.events || []);
    } catch (err) {
      console.warn('Failed to load events:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [activeTab]);

  const handleOpenCreateModal = () => {
    setEditingEventId(null);
    setFormData({
      title: '',
      event_type: 'FESTIVAL',
      description: '',
      venue_name: '',
      road_name: '',
      lat: 11.0168,
      lng: 76.9558,
      expected_crowd: 3000,
      impact_level: 'HIGH',
      start_time: new Date().toISOString().slice(0, 16),
      end_time: new Date(Date.now() + 6 * 3600 * 1000).toISOString().slice(0, 16),
    });
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (ev) => {
    setEditingEventId(ev._id);
    setFormData({
      title: ev.title || '',
      event_type: ev.event_type || 'OTHER',
      description: ev.description || '',
      venue_name: ev.venue_name || '',
      road_name: ev.road_name || '',
      lat: ev.lat || ev.location?.coordinates?.[1] || 11.0168,
      lng: ev.lng || ev.location?.coordinates?.[0] || 76.9558,
      expected_crowd: ev.expected_crowd || 500,
      impact_level: ev.impact_level || 'MEDIUM',
      start_time: ev.start_time ? new Date(ev.start_time).toISOString().slice(0, 16) : '',
      end_time: ev.end_time ? new Date(ev.end_time).toISOString().slice(0, 16) : '',
    });
    setIsModalOpen(true);
  };

  const handleDeleteEvent = async (id) => {
    if (!window.confirm('Are you sure you want to delete this event?')) return;
    try {
      await axios.delete(`/api/events/${id}`);
      setAlertMsg({ type: 'success', text: 'Event deleted successfully.' });
      fetchEvents();
    } catch (err) {
      setAlertMsg({ type: 'error', text: 'Failed to delete event.' });
    }
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingEventId) {
        await axios.put(`/api/events/${editingEventId}`, formData);
        setAlertMsg({ type: 'success', text: 'Event updated successfully.' });
      } else {
        await axios.post('/api/events', formData);
        setAlertMsg({ type: 'success', text: 'Event created successfully.' });
      }
      setIsModalOpen(false);
      fetchEvents();
    } catch (err) {
      setAlertMsg({
        type: 'error',
        text: err.response?.data?.message || 'Failed to save event.',
      });
    }
  };

  // Filter by search query
  const filteredEvents = events.filter((ev) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      ev.title?.toLowerCase().includes(q) ||
      ev.venue_name?.toLowerCase().includes(q) ||
      ev.road_name?.toLowerCase().includes(q)
    );
  });

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Top Header */}
      <header className="h-16 shrink-0 bg-slate-900/80 backdrop-blur border-b border-slate-800 px-6 flex items-center justify-between z-20">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-purple-600 to-rose-500 flex items-center justify-center shadow-lg shadow-purple-900/30">
            <Calendar className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold tracking-tight text-white">
                Events & Bottleneck Administration
              </h1>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 bg-purple-500/10 text-purple-300 border border-purple-500/20 rounded-full">
                Admin Console
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Manage Festivals, Weddings & Gatherings impacting Coimbatore traffic routes
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
            onClick={handleOpenCreateModal}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-blue-600 to-teal-500 hover:from-blue-500 hover:to-teal-400 text-white text-xs font-semibold shadow-lg shadow-blue-900/20 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            Add New Event
          </button>
        </div>
      </header>

      {/* Main Content Body */}
      <div className="flex-1 flex flex-col p-6 overflow-y-auto space-y-5">
        {/* Feedback Alert */}
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

        {/* Filter & Search Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
          {/* Tabs */}
          <div className="flex items-center gap-1 overflow-x-auto w-full sm:w-auto">
            {['ALL', 'FESTIVAL', 'MARRIAGE', 'PUBLIC_EVENT'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                  activeTab === tab
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-slate-800/80 text-slate-400 hover:text-slate-200'
                }`}
              >
                {tab.replace('_', ' ')}
              </button>
            ))}
          </div>

          {/* Search Box */}
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search event title, venue, road..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 pl-9 pr-3 py-1.5 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-blue-500 placeholder-slate-500"
            />
          </div>
        </div>

        {/* Events Grid */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Active & Scheduled Traffic Events ({filteredEvents.length})
            </h3>
            {loading && (
              <div className="flex items-center gap-1 text-xs text-blue-400 animate-pulse">
                <RefreshCw className="w-3 h-3 animate-spin" />
                Loading events...
              </div>
            )}
          </div>

          {filteredEvents.length === 0 && !loading ? (
            <div className="p-8 text-center bg-slate-900/40 rounded-xl border border-slate-800 text-slate-400 text-xs">
              No events found. Click <strong>"Add New Event"</strong> to create one.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredEvents.map((ev) => {
                if (ev.event_type === 'FESTIVAL') {
                  return (
                    <div key={ev._id} className="space-y-2">
                      <FestivalCard event={ev} />
                      <div className="flex justify-end gap-3 px-1 text-xs">
                        <button
                          onClick={() => handleOpenEditModal(ev)}
                          className="text-blue-400 hover:text-blue-300 font-medium"
                        >
                          Edit Details
                        </button>
                        <button
                          onClick={() => handleDeleteEvent(ev._id)}
                          className="text-rose-400 hover:text-rose-300 font-medium"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  );
                }
                if (ev.event_type === 'MARRIAGE') {
                  return (
                    <div key={ev._id} className="space-y-2">
                      <MarriageEventCard event={ev} />
                      <div className="flex justify-end gap-3 px-1 text-xs">
                        <button
                          onClick={() => handleOpenEditModal(ev)}
                          className="text-blue-400 hover:text-blue-300 font-medium"
                        >
                          Edit Details
                        </button>
                        <button
                          onClick={() => handleDeleteEvent(ev._id)}
                          className="text-rose-400 hover:text-rose-300 font-medium"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  );
                }
                return (
                  <EventCard
                    key={ev._id}
                    event={ev}
                    isAdmin={true}
                    onEdit={handleOpenEditModal}
                    onDelete={handleDeleteEvent}
                  />
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Add / Edit Event Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl w-full max-w-xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
              <h3 className="text-sm font-bold text-slate-100">
                {editingEventId ? 'Edit Traffic Event' : 'Create New Traffic Event'}
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-200"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleFormSubmit} className="p-6 space-y-4 overflow-y-auto flex-1 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Event Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Koniamman Temple Car Festival"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Event Type *</label>
                  <select
                    value={formData.event_type}
                    onChange={(e) => setFormData({ ...formData, event_type: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-blue-500"
                  >
                    {EVENT_TYPES.map((t) => (
                      <option key={t.value} value={t.value}>
                        {t.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 font-medium mb-1">Impact Level *</label>
                  <select
                    value={formData.impact_level}
                    onChange={(e) => setFormData({ ...formData, impact_level: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-blue-500"
                  >
                    {IMPACT_LEVELS.map((imp) => (
                      <option key={imp.value} value={imp.value}>
                        {imp.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Venue Name</label>
                  <input
                    type="text"
                    placeholder="e.g. Town Hall Chariot Route"
                    value={formData.venue_name}
                    onChange={(e) => setFormData({ ...formData, venue_name: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-medium mb-1">Expected Crowd Size</label>
                  <input
                    type="number"
                    value={formData.expected_crowd}
                    onChange={(e) => setFormData({ ...formData, expected_crowd: parseInt(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Geographic Presets */}
              <div className="space-y-1.5">
                <label className="block text-slate-400 font-medium">Quick Location Preset</label>
                <div className="flex flex-wrap gap-1.5">
                  {COIMBATORE_LANDMARKS.map((lm) => (
                    <button
                      key={lm.name}
                      type="button"
                      onClick={() => setFormData({ ...formData, lat: lm.lat, lng: lm.lng, venue_name: lm.name })}
                      className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[10px] text-slate-300 border border-slate-700 transition-colors"
                    >
                      {lm.name}
                    </button>
                  ))}
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
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-blue-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Longitude</label>
                  <input
                    type="number"
                    step="any"
                    value={formData.lng}
                    onChange={(e) => setFormData({ ...formData, lng: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-blue-500 font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Start Date & Time</label>
                  <input
                    type="datetime-local"
                    value={formData.start_time}
                    onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-medium mb-1">End Date & Time</label>
                  <input
                    type="datetime-local"
                    value={formData.end_time}
                    onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Description & Traffic Advisory</label>
                <textarea
                  rows={2}
                  placeholder="Describe road diversions, parking overflow, or chariot route..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 px-3 py-2 rounded-lg text-slate-100 focus:outline-none focus:border-blue-500"
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
                  className="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold shadow-lg shadow-blue-900/30"
                >
                  {editingEventId ? 'Update Event' : 'Create Event'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
