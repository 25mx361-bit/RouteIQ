import React, { useState } from 'react';
import {
  MapPin,
  Navigation,
  Calendar,
  Clock,
  ArrowUpDown,
  Search,
  Sparkles,
  AlertCircle,
} from 'lucide-react';
import { useGeocoding } from '../hooks/useGeocoding';

export default function SearchForm({ onLocationsResolved }) {
  const [sourceText, setSourceText] = useState('Gandhipuram');
  const [destText, setDestText] = useState('RS Puram');

  // Default to today's date & current time
  const now = new Date();
  const todayStr = now.toISOString().split('T')[0];
  const timeStr = now.toTimeString().slice(0, 5);

  const [travelDate, setTravelDate] = useState(todayStr);
  const [travelTime, setTravelTime] = useState(timeStr);

  const { geocodeLocation, loading, error, clearError, suggestions } =
    useGeocoding();

  const handleSwap = () => {
    const temp = sourceText;
    setSourceText(destText);
    setDestText(temp);
  };

  const handleQuickSelect = (src, dst) => {
    setSourceText(src);
    setDestText(dst);
    clearError();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    clearError();

    if (!sourceText.trim() || !destText.trim()) {
      return;
    }

    // Geocode both locations in parallel
    const [sourceResult, destResult] = await Promise.all([
      geocodeLocation(sourceText),
      geocodeLocation(destText),
    ]);

    if (sourceResult && destResult) {
      if (onLocationsResolved) {
        onLocationsResolved({
          source: {
            lat: sourceResult.latitude,
            lng: sourceResult.longitude,
            label: sourceResult.displayName,
          },
          destination: {
            lat: destResult.latitude,
            lng: destResult.longitude,
            label: destResult.displayName,
          },
          date: travelDate,
          time: travelTime,
        });
      }
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-5">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-100">
              Trip & Route Query
            </h2>
            <p className="text-xs text-slate-400">Coimbatore Metro Region</p>
          </div>
        </div>
        <span className="text-[10px] font-mono uppercase px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded">
          PatchTST & CatBoost Ready
        </span>
      </div>

      {error && (
        <div className="flex items-start gap-2 p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <div className="flex-1">{error}</div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Source Location */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block"></span>
            Source Location
          </label>
          <div className="relative">
            <input
              type="text"
              value={sourceText}
              onChange={(e) => setSourceText(e.target.value)}
              placeholder="e.g. Gandhipuram, Peelamedu..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
              required
            />
            <MapPin className="w-4 h-4 text-emerald-400 absolute left-3 top-3 pointer-events-none" />
          </div>
        </div>

        {/* Swap Button */}
        <div className="flex justify-center -my-2 relative z-10">
          <button
            type="button"
            onClick={handleSwap}
            title="Swap Origin & Destination"
            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-full border border-slate-700 hover:text-emerald-400 transition-all shadow-md active:scale-95"
          >
            <ArrowUpDown className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Destination Location */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-rose-400 inline-block"></span>
            Destination Location
          </label>
          <div className="relative">
            <input
              type="text"
              value={destText}
              onChange={(e) => setDestText(e.target.value)}
              placeholder="e.g. RS Puram, Airport..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors"
              required
            />
            <Navigation className="w-4 h-4 text-rose-400 absolute left-3 top-3 pointer-events-none" />
          </div>
        </div>

        {/* Date & Time Selectors */}
        <div className="grid grid-cols-2 gap-3 pt-1">
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-300 flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              Travel Date
            </label>
            <input
              type="date"
              value={travelDate}
              onChange={(e) => setTravelDate(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 transition-colors"
              required
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-300 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              Travel Time
            </label>
            <input
              type="time"
              value={travelTime}
              onChange={(e) => setTravelTime(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 transition-colors"
              required
            />
          </div>
        </div>

        {/* Quick Route Shortcuts */}
        <div className="pt-2">
          <span className="text-[11px] font-medium text-slate-400">
            Popular Coimbatore Routes:
          </span>
          <div className="flex flex-wrap gap-1.5 mt-1.5">
            <button
              type="button"
              onClick={() => handleQuickSelect('Gandhipuram', 'RS Puram')}
              className="px-2 py-1 bg-slate-800/80 hover:bg-slate-800 text-[11px] text-slate-300 rounded border border-slate-700/60 transition"
            >
              Gandhipuram ➔ RS Puram
            </button>
            <button
              type="button"
              onClick={() => handleQuickSelect('PSG Tech', 'Coimbatore Airport')}
              className="px-2 py-1 bg-slate-800/80 hover:bg-slate-800 text-[11px] text-slate-300 rounded border border-slate-700/60 transition"
            >
              PSG Tech ➔ Airport
            </button>
            <button
              type="button"
              onClick={() =>
                handleQuickSelect('Coimbatore Railway Station', 'Saravanampatti')
              }
              className="px-2 py-1 bg-slate-800/80 hover:bg-slate-800 text-[11px] text-slate-300 rounded border border-slate-700/60 transition"
            >
              Railway ➔ Saravanampatti
            </button>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full mt-2 py-2.5 px-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-medium text-xs rounded-lg shadow-lg shadow-emerald-900/30 flex items-center justify-center gap-2 transition-all active:scale-[0.98] disabled:opacity-50"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              <span>Geocoding & Locating...</span>
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              <span>Locate Points on Map</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
