import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  MapPin, Navigation, Calendar, Clock, Loader2,
  Sparkles, Compass, Search, X, CheckCircle2,
  Car, Bike, Bus, Zap
} from 'lucide-react';
import axios from 'axios';
import MapView from '../components/MapView';

const VEHICLE_OPTIONS = [
  { id: 'car', label: 'Car', icon: Car },
  { id: 'two_wheeler', label: '2-Wheeler', icon: Bike },
  { id: 'auto', label: 'Auto', icon: Car },
  { id: 'heavy', label: 'Bus / Truck', icon: Bus },
  { id: 'ev', label: 'EV', icon: Zap },
];

// ─── Inline debounce ──────────────────────────────────────────────────────────
function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

// ─── Geocode Suggestions Dropdown ─────────────────────────────────────────────
function GeoSuggest({ results, onSelect, loading }) {
  if (loading) {
    return (
      <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl shadow-xl p-3 flex items-center gap-2 text-sm text-gray-500 dark:text-slate-400">
        <Loader2 size={14} className="animate-spin text-indigo-500" />
        Searching locations…
      </div>
    );
  }
  if (!results || results.length === 0) return null;
  return (
    <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl shadow-xl overflow-hidden max-h-52 overflow-y-auto">
      {results.map((r, i) => (
        <button
          key={i}
          type="button"
          onMouseDown={(e) => { e.preventDefault(); onSelect(r); }}
          className="w-full text-left px-4 py-2.5 hover:bg-indigo-50 dark:hover:bg-slate-700 text-sm border-b border-gray-100 dark:border-slate-700 last:border-0 transition-colors"
        >
          <div className="flex items-start gap-2">
            <MapPin size={13} className="mt-0.5 shrink-0 text-indigo-400" />
            <div>
              <div className="font-semibold text-gray-800 dark:text-slate-100 line-clamp-1">{r.label}</div>
              {r.sublabel && (
                <div className="text-[11px] text-gray-400 dark:text-slate-500 line-clamp-1">{r.sublabel}</div>
              )}
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}

// ─── Main Page ─────────────────────────────────────────────────────────────────
export default function PlanRoutePage() {
  const navigate = useNavigate();
  const location = useLocation();
  const sourceRef = useRef(null);
  const destRef   = useRef(null);

  const [loading, setLoading] = useState(false);
  const [sourceInput, setSourceInput] = useState('');
  const [destInput,   setDestInput]   = useState('');

  // Resolved coordinates — null until user picks a suggestion or hits search
  const [source, setSource] = useState(null); // { lat, lng, label }
  const [dest,   setDest]   = useState(null);

  const [sourceSuggestions, setSourceSuggestions] = useState([]);
  const [destSuggestions,   setDestSuggestions]   = useState([]);
  const [sourceLoading, setSourceLoading] = useState(false);
  const [destLoading,   setDestLoading]   = useState(false);
  const [sourceFocused, setSourceFocused] = useState(false);
  const [destFocused,   setDestFocused]   = useState(false);

  const [formMeta, setFormMeta] = useState({
    date: new Date().toISOString().split('T')[0],
    time: new Date().toTimeString().slice(0, 5),
  });
  const [vehicleType, setVehicleType] = useState('car');
  const [error, setError] = useState('');

  // Prefill from navigation state if redirected from Dashboard
  useEffect(() => {
    if (location.state?.source) {
      setSource(location.state.source);
      setSourceInput(location.state.source.label || '');
    }
    if (location.state?.dest) {
      setDest(location.state.dest);
      setDestInput(location.state.dest.label || '');
    }
    if (location.state?.vehicleType) {
      setVehicleType(location.state.vehicleType);
    }
  }, [location.state]);

  const debouncedSource = useDebounce(sourceInput, 420);
  const debouncedDest   = useDebounce(destInput,   420);

  // ── Parse geocode API results into {label, sublabel, lat, lng} ──────────────
  const parseResults = (data) => {
    if (!data) return [];
    const raw = Array.isArray(data) ? data : (data.features || data.results || []);
    return raw.slice(0, 6).map((item) => {
      // Backend preset/nominatim format: { latitude, longitude, display_name }
      if (item.latitude !== undefined && item.longitude !== undefined) {
        const parts = (item.display_name || '').split(',');
        return {
          lat: parseFloat(item.latitude),
          lng: parseFloat(item.longitude),
          label: parts[0]?.trim() || item.display_name,
          sublabel: parts.slice(1, 3).join(',').trim(),
        };
      }
      // Nominatim direct format: { lat, lon, display_name }
      if (item.lat !== undefined && item.lon !== undefined) {
        const parts = (item.display_name || '').split(',');
        return {
          lat: parseFloat(item.lat),
          lng: parseFloat(item.lon),
          label: parts[0]?.trim() || item.display_name,
          sublabel: parts.slice(1, 3).join(',').trim(),
        };
      }
      // GeoJSON Feature style
      if (item.geometry?.coordinates) {
        const [lng, lat] = item.geometry.coordinates;
        return {
          lat,
          lng,
          label: item.properties?.name || item.properties?.display_name || 'Location',
          sublabel: item.properties?.display_name || '',
        };
      }
      return null;
    }).filter(Boolean);
  };

  // ── Fetch suggestions from backend geocode endpoint ─────────────────────────
  const fetchSuggestions = useCallback(async (query, setSuggestions, setGeoLoading) => {
    if (!query || query.length < 2) { setSuggestions([]); return; }
    setGeoLoading(true);
    try {
      const res = await axios.get('/api/geocode/search', { params: { q: query } });
      const parsed = parseResults(res.data);
      setSuggestions(parsed);
    } catch (err) {
      // Fallback: try Nominatim directly for the query
      try {
        const res = await axios.get('https://nominatim.openstreetmap.org/search', {
          params: { q: `${query}, Coimbatore, Tamil Nadu, India`, format: 'json', limit: 6, addressdetails: 1 },
          headers: { 'Accept-Language': 'en' }
        });
        setSuggestions(parseResults(res.data));
      } catch { setSuggestions([]); }
    } finally {
      setGeoLoading(false);
    }
  }, []);

  // ── Debounced Effects ────────────────────────────────────────────────────────
  useEffect(() => {
    // Don't re-search if the input already matches a resolved location's label
    if (source && debouncedSource === source.label) return;
    fetchSuggestions(debouncedSource, setSourceSuggestions, setSourceLoading);
  }, [debouncedSource]);

  useEffect(() => {
    if (dest && debouncedDest === dest.label) return;
    fetchSuggestions(debouncedDest, setDestSuggestions, setDestLoading);
  }, [debouncedDest]);

  // ── Select suggestion ────────────────────────────────────────────────────────
  const selectSource = (r) => {
    setSource(r);
    setSourceInput(r.label);
    setSourceSuggestions([]);
    setSourceFocused(false);
  };

  const selectDest = (r) => {
    setDest(r);
    setDestInput(r.label);
    setDestSuggestions([]);
    setDestFocused(false);
  };

  // ── Clear helpers ────────────────────────────────────────────────────────────
  const clearSource = () => { setSourceInput(''); setSource(null); setSourceSuggestions([]); sourceRef.current?.focus(); };
  const clearDest   = () => { setDestInput('');   setDest(null);   setDestSuggestions([]);   destRef.current?.focus(); };

  // ── Submit ───────────────────────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate coords are resolved
    if (!source || !source.lat || !source.lng) {
      setError('Please select a starting location from the suggestions list.');
      sourceRef.current?.focus();
      return;
    }
    if (!dest || !dest.lat || !dest.lng) {
      setError('Please select a destination from the suggestions list.');
      destRef.current?.focus();
      return;
    }
    if (Math.abs(source.lat - dest.lat) < 0.0005 && Math.abs(source.lng - dest.lng) < 0.0005) {
      setError('Source and destination cannot be the same location.');
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post('/api/routes/search', {
        source_lat:   source.lat,
        source_lng:   source.lng,
        dest_lat:     dest.lat,
        dest_lng:     dest.lng,
        source_label: source.label,
        dest_label:   dest.label,
        date:         formMeta.date,
        time:         formMeta.time,
        vehicle_type: vehicleType,
      });
      const resultWithVehicle = { ...res.data, vehicle_type: vehicleType };
      sessionStorage.setItem('routeiq_search_result', JSON.stringify(resultWithVehicle));
      navigate('/predictions');
    } catch (err) {
      const msg = err?.response?.data?.error || err?.response?.data?.message || err.message || 'Route search failed.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  // Map preview coords
  const previewSource = source ? { lat: source.lat, lng: source.lng, label: source.label } : null;
  const previewDest   = dest   ? { lat: dest.lat,   lng: dest.lng,   label: dest.label   } : null;
  const mapCenter = previewSource || { lat: 11.0176, lng: 76.9667, label: 'Coimbatore' };

  return (
    <div className="flex flex-col lg:flex-row h-full bg-gray-50 dark:bg-slate-950 transition-colors duration-200">
      {/* ── Left Panel ── */}
      <div className="w-full lg:w-[430px] border-b lg:border-b-0 lg:border-r border-gray-200 dark:border-slate-800 p-6 flex flex-col h-full bg-white dark:bg-slate-900 shadow-lg z-10 overflow-y-auto">
        {/* Header */}
        <div className="flex items-center gap-2 mb-6">
          <div className="w-9 h-9 rounded-xl bg-indigo-100 dark:bg-indigo-950/70 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-800 dark:text-slate-100">Plan Optimal Route</h1>
            <p className="text-xs text-gray-400 dark:text-slate-500">Traffic Forecasting &amp; Safety Analysis</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5 flex-1 flex flex-col justify-between">
          <div className="space-y-4">

            {/* ── Source Input ── */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-slate-400 mb-1.5">
                Starting Location
              </label>
              <div className="relative">
                {source ? (
                  <CheckCircle2 className="absolute left-3.5 top-3.5 text-emerald-500" size={18} />
                ) : (
                  <MapPin className="absolute left-3.5 top-3.5 text-indigo-500" size={18} />
                )}
                <input
                  ref={sourceRef}
                  type="text"
                  value={sourceInput}
                  onChange={(e) => { setSourceInput(e.target.value); if (source) setSource(null); }}
                  onFocus={() => setSourceFocused(true)}
                  onBlur={() => setTimeout(() => setSourceFocused(false), 180)}
                  className={`pl-10 pr-8 w-full p-3 bg-gray-50 dark:bg-slate-800 border rounded-xl text-sm font-medium text-gray-800 dark:text-slate-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all ${source ? 'border-emerald-400 dark:border-emerald-600' : 'border-gray-200 dark:border-slate-700'}`}
                  placeholder="Type to search — e.g. Peelamedu"
                  autoComplete="off"
                />
                {sourceInput && (
                  <button type="button" onClick={clearSource} className="absolute right-3 top-3.5 text-gray-400 hover:text-gray-600 dark:hover:text-slate-300">
                    <X size={16} />
                  </button>
                )}
                {sourceFocused && (
                  <GeoSuggest
                    results={sourceSuggestions}
                    onSelect={selectSource}
                    loading={sourceLoading && debouncedSource.length > 1}
                  />
                )}
              </div>
              {source && (
                <p className="mt-1 text-[11px] text-emerald-600 dark:text-emerald-400 font-medium px-1">
                  ✓ {source.lat.toFixed(4)}, {source.lng.toFixed(4)}
                </p>
              )}
            </div>

            {/* ── Destination Input ── */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-slate-400 mb-1.5">
                Destination Location
              </label>
              <div className="relative">
                {dest ? (
                  <CheckCircle2 className="absolute left-3.5 top-3.5 text-rose-500" size={18} />
                ) : (
                  <Navigation className="absolute left-3.5 top-3.5 text-emerald-500" size={18} />
                )}
                <input
                  ref={destRef}
                  type="text"
                  value={destInput}
                  onChange={(e) => { setDestInput(e.target.value); if (dest) setDest(null); }}
                  onFocus={() => setDestFocused(true)}
                  onBlur={() => setTimeout(() => setDestFocused(false), 180)}
                  className={`pl-10 pr-8 w-full p-3 bg-gray-50 dark:bg-slate-800 border rounded-xl text-sm font-medium text-gray-800 dark:text-slate-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all ${dest ? 'border-rose-400 dark:border-rose-600' : 'border-gray-200 dark:border-slate-700'}`}
                  placeholder="Type to search — e.g. Hopes"
                  autoComplete="off"
                />
                {destInput && (
                  <button type="button" onClick={clearDest} className="absolute right-3 top-3.5 text-gray-400 hover:text-gray-600 dark:hover:text-slate-300">
                    <X size={16} />
                  </button>
                )}
                {destFocused && (
                  <GeoSuggest
                    results={destSuggestions}
                    onSelect={selectDest}
                    loading={destLoading && debouncedDest.length > 1}
                  />
                )}
              </div>
              {dest && (
                <p className="mt-1 text-[11px] text-rose-600 dark:text-rose-400 font-medium px-1">
                  ✓ {dest.lat.toFixed(4)}, {dest.lng.toFixed(4)}
                </p>
              )}
            </div>

            {/* ── Date & Time ── */}
            <div className="grid grid-cols-2 gap-3 pt-1">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-slate-400 mb-1.5">
                  Travel Date
                </label>
                <div className="relative">
                  <Calendar className="absolute left-3.5 top-3.5 text-gray-400" size={18} />
                  <input
                    type="date"
                    value={formMeta.date}
                    onChange={(e) => setFormMeta({ ...formMeta, date: e.target.value })}
                    className="pl-10 w-full p-3 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl text-sm font-medium text-gray-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-slate-400 mb-1.5">
                  Target Time
                </label>
                <div className="relative">
                  <Clock className="absolute left-3.5 top-3.5 text-gray-400" size={18} />
                  <input
                    type="time"
                    value={formMeta.time}
                    onChange={(e) => setFormMeta({ ...formMeta, time: e.target.value })}
                    className="pl-10 w-full p-3 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl text-sm font-medium text-gray-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                    required
                  />
                </div>
              </div>
            </div>

            {/* ── Vehicle Type Selector ── */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-slate-400 mb-1.5">
                Vehicle Type &amp; Mode
              </label>
              <div className="grid grid-cols-5 gap-1.5">
                {VEHICLE_OPTIONS.map((v) => {
                  const Icon = v.icon;
                  const isSel = vehicleType === v.id;
                  return (
                    <button
                      key={v.id}
                      type="button"
                      onClick={() => setVehicleType(v.id)}
                      className={`flex flex-col items-center justify-center p-2 rounded-xl border text-center transition-all ${
                        isSel
                          ? 'bg-indigo-50 dark:bg-indigo-950/80 border-indigo-600 dark:border-indigo-500 text-indigo-700 dark:text-indigo-300 font-bold shadow-sm ring-1 ring-indigo-500/20'
                          : 'bg-gray-50 dark:bg-slate-800 border-gray-200 dark:border-slate-700 text-gray-600 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-slate-750'
                      }`}
                    >
                      <Icon size={16} className={`mb-1 ${isSel ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500 dark:text-slate-400'}`} />
                      <span className="text-[10px] leading-tight font-medium truncate w-full">{v.label}</span>
                    </button>
                  );
                })}
              </div>
              <p className="mt-1 text-[10.5px] text-gray-400 dark:text-slate-500 italic">
                {vehicleType === 'two_wheeler' && '🛵 Optimized for agile traffic filtering & bypass roads (e.g. Thanneerpanthal Rd).'}
                {vehicleType === 'car' && '🚗 Standard car routing prioritizing smooth multilane arterials.'}
                {vehicleType === 'auto' && '🛺 Urban agility with city speed regulation (45 km/h cap).'}
                {vehicleType === 'heavy' && '🚌 Restricted to wide arterial thoroughfares; avoids narrow residential lanes.'}
                {vehicleType === 'ev' && '⚡ Eco-efficient routing favoring regenerative braking and zero tailpipe emissions.'}
              </p>
            </div>

            {/* Error */}
            {error && (
              <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-xs text-red-700 dark:text-red-300 font-medium flex items-start gap-2">
                <X size={14} className="mt-0.5 shrink-0" />
                {error}
              </div>
            )}

            {/* Info box */}
            <div className="p-3.5 rounded-xl bg-indigo-50/70 dark:bg-slate-800/60 border border-indigo-100 dark:border-slate-700 text-xs text-indigo-800 dark:text-indigo-300 flex items-start gap-2.5">
              <Sparkles className="w-4 h-4 shrink-0 text-indigo-600 dark:text-indigo-400 mt-0.5" />
              <p className="leading-relaxed">
                RouteIQ synthesizes live TomTom flow, Open-Meteo precipitation, and active hazard alerts to score candidate corridors.
              </p>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !source || !dest}
            className="w-full mt-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white p-4 rounded-xl font-bold transition-all shadow-lg shadow-indigo-500/20 active:scale-98 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={18} />
                <span>Running PatchTST &amp; CatBoost…</span>
              </>
            ) : (
              <>
                <Search size={18} />
                <span>Find Best Route</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* ── Right Map Canvas ── */}
      <div className="flex-1 bg-slate-900 relative min-h-[350px]">
        <MapView
          sourceCoords={previewSource}
          destCoords={previewDest}
          routes={[]}
        />
        {/* Placeholder overlay when no locations selected */}
        {!source && !dest && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="bg-slate-900/80 backdrop-blur-md border border-slate-700 rounded-2xl px-6 py-4 text-center shadow-2xl">
              <MapPin className="mx-auto mb-2 text-indigo-400" size={28} />
              <p className="text-slate-200 text-sm font-semibold">Search a route to preview on map</p>
              <p className="text-slate-400 text-xs mt-1">Type any Coimbatore location above</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
