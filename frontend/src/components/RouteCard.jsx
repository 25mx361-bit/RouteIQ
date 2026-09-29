import React from 'react';
import {
  Navigation,
  Clock,
  Milestone,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ShieldAlert,
  Ban,
} from 'lucide-react';

export default function RouteCard({
  route,
  index,
  isSelected,
  onSelect,
}) {
  const isBlocked = route.is_blocked || (route.landslide_hazard && route.landslide_hazard.blocked);
  const isRecommended = !isBlocked && (route.is_recommended || index === 0);

  return (
    <div
      onClick={() => {
        if (!isBlocked && onSelect) {
          onSelect(index);
        }
      }}
      className={`group relative rounded-2xl border p-4 transition-all select-none ${
        isBlocked
          ? 'bg-rose-50 dark:bg-red-950/20 border-rose-300 dark:border-red-500/40 opacity-80 cursor-not-allowed'
          : isSelected
          ? 'bg-indigo-50/80 dark:bg-slate-900 border-indigo-500 dark:border-blue-500/80 shadow-md dark:shadow-blue-950/40 ring-1 ring-indigo-500/40 dark:ring-blue-500/50 cursor-pointer'
          : 'bg-white dark:bg-slate-900/60 border-gray-200 dark:border-slate-800/80 hover:bg-gray-50/80 dark:hover:bg-slate-900 hover:border-gray-300 dark:hover:border-slate-700 shadow-sm cursor-pointer'
      }`}
    >
      {/* Top Header & Badges */}
      <div className="flex items-center justify-between gap-2 mb-2.5">
        <div className="flex items-center gap-2 min-w-0">
          <span
            className={`w-2.5 h-2.5 rounded-full shrink-0 ${
              isBlocked
                ? 'bg-rose-500 ring-4 ring-rose-500/20'
                : isSelected
                ? 'bg-indigo-600 dark:bg-blue-400 ring-4 ring-indigo-500/20 dark:ring-blue-400/20'
                : 'bg-gray-400 dark:bg-slate-500'
            }`}
          ></span>
          <h4
            className={`text-xs font-bold truncate ${
              isBlocked
                ? 'text-rose-600 dark:text-red-300 line-through'
                : isSelected
                ? 'text-indigo-700 dark:text-blue-200'
                : 'text-gray-900 dark:text-slate-200 group-hover:text-indigo-600 dark:group-hover:text-white'
            }`}
          >
            {route.name || `Route Option ${index + 1}`}
          </h4>
        </div>

        {isBlocked ? (
          <span className="shrink-0 px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 dark:bg-red-500/20 text-rose-700 dark:text-red-400 border border-rose-300 dark:border-red-500/50 flex items-center gap-1">
            <Ban className="w-3 h-3" />
            BLOCKED
          </span>
        ) : isRecommended ? (
          <span className="shrink-0 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/30 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            Recommended
          </span>
        ) : (
          <span className="shrink-0 px-2 py-0.5 rounded-full text-[10px] font-medium bg-gray-100 dark:bg-slate-800 text-gray-600 dark:text-slate-400 border border-gray-200 dark:border-slate-700">
            Alt #{index}
          </span>
        )}
      </div>

      {/* Blockage Notice if Blocked */}
      {isBlocked && (
        <div className="mb-2.5 p-2 bg-rose-50 dark:bg-red-500/10 border border-rose-200 dark:border-red-500/30 rounded-xl text-[11px] text-rose-700 dark:text-red-300 flex items-center gap-1.5 font-medium">
          <ShieldAlert className="w-3.5 h-3.5 text-rose-600 dark:text-red-400 shrink-0" />
          <span>Closed due to Landslide debris. Do not travel.</span>
        </div>
      )}

      {/* Metrics Row: Distance & Duration */}
      <div className="grid grid-cols-2 gap-2 py-2 px-3 rounded-xl bg-gray-50 dark:bg-slate-950/80 border border-gray-100 dark:border-slate-800/60 text-xs">
        <div className="flex items-center gap-2 text-gray-700 dark:text-slate-300">
          <Milestone className="w-3.5 h-3.5 text-indigo-500 dark:text-slate-400 shrink-0" />
          <div>
            <div className="text-[10px] text-gray-400 dark:text-slate-500 uppercase font-semibold">Distance</div>
            <div className="font-bold text-gray-900 dark:text-slate-200">
              {route.distance_km ? `${route.distance_km} km` : `${(route.distance_m / 1000).toFixed(1)} km`}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 text-gray-700 dark:text-slate-300">
          <Clock className="w-3.5 h-3.5 text-indigo-500 dark:text-slate-400 shrink-0" />
          <div>
            <div className="text-[10px] text-gray-400 dark:text-slate-500 uppercase font-semibold">Est. Duration</div>
            <div className="font-bold text-gray-900 dark:text-slate-200">
              {route.duration_min ? `${Math.round(route.duration_min)} mins` : `${Math.round(route.duration_s / 60)} mins`}
            </div>
          </div>
        </div>
      </div>

      {/* Road / Corridor Type & Selection prompt */}
      <div className="mt-2.5 flex items-center justify-between text-[11px]">
        <span className="text-gray-500 dark:text-slate-400 truncate max-w-[220px]">
          {route.road_type || 'Via Standard Arterial Link'}
        </span>

        {isBlocked ? (
          <span className="text-rose-600 dark:text-red-400 font-semibold text-[10px]">Hazard Closed</span>
        ) : (
          <span
            className={`flex items-center gap-1 font-semibold transition-colors ${
              isSelected ? 'text-indigo-600 dark:text-blue-400' : 'text-gray-400 dark:text-slate-500 group-hover:text-indigo-600 dark:group-hover:text-slate-300'
            }`}
          >
            {isSelected ? 'Active Route' : 'Select'}
            <ArrowRight className="w-3 h-3" />
          </span>
        )}
      </div>
    </div>
  );
}
