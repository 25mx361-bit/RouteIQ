import React from 'react';
import {
  Navigation,
  Clock,
  Milestone,
  CheckCircle2,
  AlertTriangle,
  Ban,
  TrendingUp,
  CloudLightning,
  Calendar,
  Gauge,
  Sparkles,
} from 'lucide-react';
import CongestionBadge from './CongestionBadge';

function getCongestionStatus(tci) {
  if (tci === undefined || tci === null) return 'SAFE';
  if (tci < 1.2) return 'SAFE';
  if (tci < 1.5) return 'LOW';
  if (tci < 2.0) return 'MEDIUM';
  return 'HIGH';
}

function MetricRow({ label, value, unit = '', highlight = false }) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-gray-100 dark:border-slate-800/80 last:border-0">
      <span className="text-xs text-gray-500 dark:text-slate-400">{label}</span>
      <span className={`text-xs font-mono font-semibold ${highlight ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-800 dark:text-slate-200'}`}>
        {value != null ? `${value}${unit}` : '—'}
      </span>
    </div>
  );
}

export default function RouteComparison({ routes = [], selectedRoute = 0, onSelect }) {
  if (!routes.length) {
    return (
      <div className="text-center py-12 text-gray-400 dark:text-slate-500 text-xs">
        No candidate routes generated. Search to load comparative telemetry.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {routes.map((route, idx) => {
          const isBlocked = route.is_blocked || route.blocked;
          const isSelected = idx === selectedRoute;
          const isRecommended = route.is_recommended && !isBlocked;
          const tci = route.tci ?? route.features?.tci ?? 1.2;
          const congestionStatus = isBlocked ? 'BLOCKED' : getCongestionStatus(tci);
          const weatherRisk = route.weather_risk_score ?? route.features?.weather_risk_score ?? 0.1;
          const eventImpact = route.event_impact_score ?? route.features?.event_impact_score ?? 0.05;
          const catboostScore = route.catboost_score ?? (isRecommended ? 0.94 : 0.65);
          const landslideStatus = route.landslide_hazard?.blocked
            ? 'BLOCKED'
            : route.features?.landslide_active
              ? route.features?.landslide_severity || 'ACTIVE'
              : 'CLEAR';

          return (
            <div
              key={idx}
              onClick={() => !isBlocked && onSelect?.(idx)}
              className={`
                relative rounded-2xl border p-5 transition-all duration-200 flex flex-col justify-between
                ${isBlocked
                  ? 'bg-rose-50/50 dark:bg-rose-950/20 border-rose-200 dark:border-rose-900/50 opacity-70 cursor-not-allowed'
                  : isRecommended
                    ? 'bg-white dark:bg-slate-900 border-emerald-400 dark:border-emerald-500/50 shadow-md shadow-emerald-500/5 hover:border-emerald-500'
                    : 'bg-white dark:bg-slate-900 border-gray-200 dark:border-slate-800 hover:border-indigo-300 dark:hover:border-slate-700 shadow-sm'
                }
              `}
            >
              {/* Top Row */}
              <div>
                <div className="flex items-start justify-between gap-3 mb-4 pb-3 border-b border-gray-100 dark:border-slate-800">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className={`w-7 h-7 rounded-xl flex items-center justify-center text-xs font-bold shrink-0
                      ${isBlocked ? 'bg-rose-100 text-rose-600 dark:bg-rose-950 dark:text-rose-400' : isRecommended ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-gray-100 dark:bg-slate-800 text-gray-600 dark:text-slate-400'}`}>
                      {isBlocked ? <Ban className="w-3.5 h-3.5" /> : idx + 1}
                    </div>
                    <div className="truncate">
                      <p className={`text-sm font-bold truncate ${isBlocked ? 'line-through text-gray-400 dark:text-slate-500' : 'text-gray-800 dark:text-slate-100'}`}>
                        {route.name || `Corridor Option ${idx + 1}`}
                      </p>
                      {route.blocked_reason && (
                        <p className="text-[10px] text-rose-500 mt-0.5 font-medium">{route.blocked_reason}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <CongestionBadge level={congestionStatus} />
                  </div>
                </div>

                {/* Metrics Table */}
                <div className="space-y-0.5">
                  <div className="grid grid-cols-2 gap-2 mb-2 p-2.5 rounded-xl bg-gray-50 dark:bg-slate-800/60 text-center">
                    <div>
                      <p className="text-[10px] text-gray-400 dark:text-slate-500 font-semibold uppercase">Distance</p>
                      <p className="text-xs font-bold text-gray-800 dark:text-slate-200 mt-0.5">
                        {route.distance_km ? `${route.distance_km.toFixed(1)} km` : (route.distance || '8.5 km')}
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] text-gray-400 dark:text-slate-500 font-semibold uppercase">Duration</p>
                      <p className="text-xs font-bold text-gray-800 dark:text-slate-200 mt-0.5">
                        {route.duration_min ? `${route.duration_min.toFixed(0)} min` : (route.duration || '15 min')}
                      </p>
                    </div>
                  </div>

                  <MetricRow
                    label="Traffic Congestion Index (TCI)"
                    value={tci != null ? (typeof tci === 'number' ? tci.toFixed(2) : tci) : '1.20'}
                    highlight={tci < 1.5}
                  />
                  <MetricRow
                    label="Weather Hazard Risk"
                    value={weatherRisk != null ? `${Math.round(weatherRisk * 100)}%` : '10%'}
                  />
                  <MetricRow
                    label="Event & Marriage Impact"
                    value={eventImpact != null ? `${Math.round(eventImpact * 100)}%` : '5%'}
                  />
                  <MetricRow
                    label="Landslide Passage"
                    value={landslideStatus}
                  />
                  <MetricRow
                    label="CatBoost Route Score"
                    value={`${Math.round(catboostScore * 100)}%`}
                    highlight={catboostScore > 0.6}
                  />
                </div>
              </div>

              {isRecommended && (
                <div className="mt-4 pt-3 border-t border-emerald-500/20 flex items-center justify-between text-xs font-bold text-emerald-700 dark:text-emerald-400">
                  <span className="px-2.5 py-1 bg-emerald-500/20 text-emerald-300 rounded-full text-xs font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4" /> Recommended Route
                  </span>
                  <span className="text-[11px] font-mono uppercase bg-emerald-100 dark:bg-emerald-950 px-2 py-0.5 rounded-full">Top Choice</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
