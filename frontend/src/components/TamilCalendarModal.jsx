import React, { useState, useEffect } from 'react';
import {
  Calendar,
  X,
  Sparkles,
  Search,
  Filter,
  MapPin,
  Clock,
  Users,
  AlertTriangle,
  CheckCircle,
  Plus,
  Loader2,
  Tag,
} from 'lucide-react';
import { eventsApi } from '../services/api';

const CATEGORIES = [
  { id: 'ALL', label: 'All Occasions', icon: '🗓️' },
  { id: 'MARRIAGE', label: '💍 Subha Muhurtham (சுப முகூர்த்தம்)', icon: '💍' },
  { id: 'FESTIVAL', label: '🪔 Tamil Festivals (பண்டிகைகள்)', icon: '🪔' },
  { id: 'TEMPLE_OCCASION', label: '🛕 Temple Car Festivals (தேர்த் திருவிழா)', icon: '🛕' },
];

export default function TamilCalendarModal({ isOpen, onClose, onEventActivated, existingEvents = [] }) {
  const [loading, setLoading] = useState(false);
  const [activatingId, setActivatingId] = useState(null);
  const [occasions, setOccasions] = useState([]);
  const [months, setMonths] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedMonth, setSelectedMonth] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [feedbackMsg, setFeedbackMsg] = useState(null);

  // Set of titles of existing active events to indicate already active
  const existingTitles = new Set(
    existingEvents.map((e) => (e.title || '').trim().toLowerCase())
  );

  useEffect(() => {
    if (!isOpen) return;
    loadTamilCalendar();
  }, [isOpen, selectedCategory, selectedMonth]);

  const loadTamilCalendar = async () => {
    setLoading(true);
    try {
      const res = await eventsApi.getTamilCalendar({
        category: selectedCategory,
        month: selectedMonth,
      });
      setOccasions(res.data?.events || []);
      if (res.data?.months && months.length === 0) {
        setMonths(res.data.months);
      }
    } catch (err) {
      console.error('Failed to load Tamil calendar:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleActivate = async (occ) => {
    setActivatingId(occ.id);
    setFeedbackMsg(null);
    try {
      await eventsApi.activateTamilEvent({
        id: occ.id,
        title: occ.title,
        tamil_title: occ.tamil_title,
        tamil_month: occ.tamil_month,
        category: occ.category,
        event_type: occ.event_type || occ.category,
        date: occ.date,
        venue_name: occ.venue_name,
        road_name: occ.road_name,
        lat: occ.lat,
        lng: occ.lng,
        expected_crowd: occ.expected_crowd,
        impact_level: occ.impact_level,
        affected_corridors: occ.affected_corridors || [],
        description: occ.description,
        muhurtham_time: occ.muhurtham_time || occ.timing,
        nakshatram: occ.nakshatram,
        tithi: occ.tithi,
      });

      setFeedbackMsg({
        type: 'success',
        text: `"${occ.title}" successfully added to live Coimbatore traffic monitoring!`,
      });

      if (onEventActivated) {
        onEventActivated();
      }
    } catch (err) {
      console.error('Failed to activate occasion:', err);
      setFeedbackMsg({
        type: 'error',
        text: err.response?.data?.message || 'Failed to activate event into traffic system.',
      });
    } finally {
      setActivatingId(null);
    }
  };

  if (!isOpen) return null;

  // Client-side search filtering
  const filteredOccasions = occasions.filter((occ) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      occ.title?.toLowerCase().includes(q) ||
      occ.tamil_title?.toLowerCase().includes(q) ||
      occ.venue_name?.toLowerCase().includes(q) ||
      occ.road_name?.toLowerCase().includes(q) ||
      occ.affected_corridors?.some((c) => c.toLowerCase().includes(q))
    );
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-3xl w-full max-w-5xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden transition-colors">
        
        {/* Header */}
        <div className="p-6 border-b border-gray-100 dark:border-slate-800 flex items-start justify-between bg-gradient-to-r from-amber-500/10 via-purple-500/10 to-transparent">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-amber-500 text-white flex items-center justify-center shadow-lg shadow-amber-500/30">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-gray-900 dark:text-slate-100">
                  Tamil Calendar & Occasions (தமிழ் நாட்காட்டி)
                </h3>
                <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-700">
                  Coimbatore Corridor Registry
                </span>
              </div>
              <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">
                Auspicious Subha Muhurtham dates, Hindu/Christian/Muslim festivals, and temple car processions impacting Coimbatore traffic
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 dark:text-slate-400 dark:hover:text-slate-200 rounded-xl hover:bg-gray-100 dark:hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Feedback Alert */}
        {feedbackMsg && (
          <div
            className={`mx-6 mt-4 p-3.5 rounded-2xl text-xs flex items-center justify-between border ${
              feedbackMsg.type === 'success'
                ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300'
                : 'bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              <span>{feedbackMsg.text}</span>
            </div>
            <button onClick={() => setFeedbackMsg(null)}>
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Filters Bar */}
        <div className="p-4 border-b border-gray-100 dark:border-slate-800 bg-gray-50/50 dark:bg-slate-900/50 flex flex-col md:flex-row items-center gap-3">
          {/* Category Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0">
            {CATEGORIES.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition cursor-pointer ${
                  selectedCategory === cat.id
                    ? 'bg-amber-600 dark:bg-amber-500 text-white shadow-sm'
                    : 'bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 text-gray-600 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-700'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2 w-full md:w-auto md:ml-auto">
            {/* Tamil Month Selector */}
            <select
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
              className="bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 px-3 py-1.5 rounded-xl text-xs text-gray-700 dark:text-slate-200 focus:outline-none focus:border-amber-500 transition cursor-pointer"
            >
              <option value="ALL">All Tamil Months (அனைத்து மாதங்கள்)</option>
              {months.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.tamil} ({m.english}) — {m.period}
                </option>
              ))}
            </select>

            {/* Search Box */}
            <div className="relative flex-1 md:w-56">
              <Search className="w-3.5 h-3.5 text-gray-400 dark:text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search mandapam, temple, road..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 pl-8 pr-3 py-1.5 rounded-xl text-xs text-gray-900 dark:text-slate-100 placeholder-gray-400 dark:placeholder-slate-500 focus:outline-none focus:border-amber-500 transition"
              />
            </div>
          </div>
        </div>

        {/* Occasions List */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {loading ? (
            <div className="py-20 flex flex-col items-center justify-center text-gray-400 dark:text-slate-500 gap-2">
              <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
              <span className="text-xs">Loading authentic Tamil calendar occasions...</span>
            </div>
          ) : filteredOccasions.length === 0 ? (
            <div className="py-20 text-center text-gray-400 dark:text-slate-500 text-xs">
              No Tamil occasions found matching the selected filter criteria.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredOccasions.map((occ) => {
                const isAlreadyActive =
                  existingTitles.has((occ.title || '').trim().toLowerCase()) ||
                  existingTitles.has((occ.tamil_title || '').trim().toLowerCase());
                const isActivating = activatingId === occ.id;

                const isMuhurtham = occ.category === 'MARRIAGE';
                const isFestival = occ.category === 'FESTIVAL';
                const isTemple = occ.category === 'TEMPLE_OCCASION';

                return (
                  <div
                    key={occ.id}
                    className={`rounded-2xl border p-5 flex flex-col justify-between transition hover:shadow-md ${
                      isAlreadyActive
                        ? 'bg-emerald-50/40 dark:bg-emerald-950/20 border-emerald-300 dark:border-emerald-800'
                        : 'bg-white dark:bg-slate-800/80 border-gray-200 dark:border-slate-700'
                    }`}
                  >
                    <div>
                      {/* Top Badges */}
                      <div className="flex items-center justify-between gap-2 mb-2.5">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                              isMuhurtham
                                ? 'bg-pink-100 dark:bg-pink-950/70 text-pink-700 dark:text-pink-300 border border-pink-200 dark:border-pink-800'
                                : isFestival
                                ? 'bg-amber-100 dark:bg-amber-950/70 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800'
                                : 'bg-orange-100 dark:bg-orange-950/70 text-orange-800 dark:text-orange-300 border border-orange-200 dark:border-orange-800'
                            }`}
                          >
                            {occ.category_label || occ.category}
                          </span>

                          {occ.tamil_month && (
                            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                              {occ.tamil_month}
                            </span>
                          )}
                        </div>

                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            occ.impact_level === 'CRITICAL'
                              ? 'bg-rose-100 dark:bg-rose-950/70 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800'
                              : occ.impact_level === 'HIGH'
                              ? 'bg-amber-100 dark:bg-amber-950/70 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800'
                              : 'bg-blue-100 dark:bg-blue-950/70 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800'
                          }`}
                        >
                          {occ.impact_level} IMPACT
                        </span>
                      </div>

                      {/* Titles */}
                      <h4 className="text-sm font-bold text-gray-900 dark:text-slate-100 leading-snug">
                        {occ.title}
                      </h4>
                      {occ.tamil_title && (
                        <p className="text-xs font-semibold text-amber-700 dark:text-amber-400 mt-0.5">
                          {occ.tamil_title}
                        </p>
                      )}

                      {/* Timings / Muhurtham Details */}
                      <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-gray-600 dark:text-slate-300 bg-gray-50 dark:bg-slate-900/60 p-3 rounded-xl border border-gray-100 dark:border-slate-800">
                        <div className="flex items-center gap-1.5">
                          <Calendar className="w-3.5 h-3.5 text-gray-400 dark:text-slate-500 shrink-0" />
                          <span className="font-semibold text-gray-800 dark:text-slate-200">
                            {occ.date}
                          </span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                          <span className="truncate">
                            {occ.muhurtham_time || occ.timing || 'All Day Occasion'}
                          </span>
                        </div>

                        {occ.nakshatram && (
                          <div className="col-span-1 sm:col-span-2 text-[11px] text-gray-500 dark:text-slate-400 border-t border-gray-100 dark:border-slate-800 pt-1.5 mt-0.5 flex items-center justify-between">
                            <span>நட்சத்திரம்: <strong className="text-gray-700 dark:text-slate-200">{occ.nakshatram}</strong></span>
                            {occ.tithi && <span>திதி: <strong className="text-gray-700 dark:text-slate-200">{occ.tithi}</strong></span>}
                          </div>
                        )}
                      </div>

                      {/* Venue & Corridors */}
                      <div className="mt-3 space-y-1.5 text-xs text-gray-600 dark:text-slate-300">
                        <div className="flex items-start gap-1.5">
                          <MapPin className="w-3.5 h-3.5 text-rose-500 shrink-0 mt-0.5" />
                          <span>
                            <strong>{occ.venue_name}</strong> • {occ.road_name}
                          </span>
                        </div>

                        {occ.affected_corridors && occ.affected_corridors.length > 0 && (
                          <div className="flex items-center gap-1 flex-wrap pt-1">
                            <Tag className="w-3 h-3 text-gray-400 dark:text-slate-500 shrink-0" />
                            <span className="text-[10px] text-gray-400 dark:text-slate-500 mr-1">Choke Corridors:</span>
                            {occ.affected_corridors.map((c, i) => (
                              <span
                                key={i}
                                className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 dark:bg-slate-700 text-gray-600 dark:text-slate-300 font-medium"
                              >
                                {c}
                              </span>
                            ))}
                          </div>
                        )}

                        <p className="text-[11px] text-gray-500 dark:text-slate-400 pt-1 line-clamp-2">
                          {occ.description}
                        </p>
                      </div>
                    </div>

                    {/* Footer Action Button */}
                    <div className="mt-4 pt-3 border-t border-gray-100 dark:border-slate-800 flex items-center justify-between">
                      <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-slate-400">
                        <Users className="w-3.5 h-3.5" />
                        <span>~{(occ.expected_crowd || 1000).toLocaleString()} expected</span>
                      </div>

                      {isAlreadyActive ? (
                        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 text-xs font-bold border border-emerald-300 dark:border-emerald-700">
                          <CheckCircle className="w-3.5 h-3.5" />
                          <span>Active in RouteIQ</span>
                        </div>
                      ) : (
                        <button
                          onClick={() => handleActivate(occ)}
                          disabled={isActivating}
                          className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 text-white text-xs font-bold shadow-md shadow-amber-600/20 transition disabled:opacity-50 cursor-pointer"
                        >
                          {isActivating ? (
                            <>
                              <Loader2 className="w-3.5 h-3.5 animate-spin" />
                              <span>Activating...</span>
                            </>
                          ) : (
                            <>
                              <Plus className="w-3.5 h-3.5" />
                              <span>Add to Live Traffic Events</span>
                            </>
                          )}
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-gray-100 dark:border-slate-800 bg-gray-50/50 dark:bg-slate-900/50 flex items-center justify-between text-xs text-gray-500 dark:text-slate-400">
          <span>Showing {filteredOccasions.length} authentic Tamil Calendar occasions</span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-700 dark:text-slate-200 hover:bg-gray-100 dark:hover:bg-slate-700 font-semibold transition"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
