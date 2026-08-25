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

/**
 * RouteComparison — card-based visual comparison for all routes.
 * Displays all features from Phase 13 feature vector and CatBoost score.
 *
 * Props:
 *   routes       — array of route objects from backend
 *   selectedRoute — index of currently selected route
 *   onSelect      — callback(index)
 */

const STATUS_CONFIG = {
  SAFE: { label: 'SAFE', bg: 'bg-emerald-500/15', border: 'border-emerald-500/40', text: 'text-emerald-400' },
  LOW: { label: 'LOW', bg: 'bg-blue-500/15', border: 'border-blue-500/40', text: 'text-blue-400' },
  MEDIUM: { label: 'MEDIUM', bg: 'bg-amber-500/15', border: 'border-amber-500/40', text: 'text-amber-400' },
  HIGH: { label: 'HIGH', bg: 'bg-orange-500/15', border: 'border-orange-500/40', text: 'text-orange-400' },
  BLOCKED: { label: 'BLOCKED', bg: 'bg-rose-500/15', border: 'border-rose-500/40', text: 'text-rose-400' },
};

function getCongestionStatus(tci) {
  if (tci === undefined || tci === null) return 'SAFE';
  if (tci < 1.2) return 'SAFE';
  if (tci < 1.5) return 'LOW';
  if (tci < 2.0) return 'MEDIUM';
  return 'HIGH';
}

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.SAFE;
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${cfg.bg} ${cfg.border} ${cfg.text}`}>
      {cfg.label}
    </span>
  );
}

function MetricRow({ label, value, unit = '', highlight = false }) {
  return (
    <div className="flex items-center justify-between py-1 border-b border-slate-800/60 last:border-0">
      <span className="text-[11px] text-slate-500">{label}</span>
      <span className={`text-[11px] font-mono font-semibold ${highlight ? 'text-teal-400' : 'text-slate-300'}`}>
        {value != null ? `${value}${unit}` : '—'}
      </span>
    </div>
  );
}

export default function RouteComparison({ routes = [], selectedRoute = 0, onSelect }) {
  if (!routes.length) {
    return (
      <div className="text-center py-12 text-slate-500 text-sm">
        Search for routes to see comparison.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
        <Sparkles className="w-3.5 h-3.5 text-teal-400" />
        Route Comparison ({routes.length} alternatives)
      </h3>

      <div className="grid grid-cols-1 gap-3">
        {routes.map((route, idx) => {
          const isBlocked = route.is_blocked;
          const isSelected = idx === selectedRoute;
          const isRecommended = route.is_recommended && !isBlocked;
          const tci = route.tci ?? route.features?.tci;
          const congestionStatus = isBlocked ? 'BLOCKED' : getCongestionStatus(tci);
          const weatherRisk = route.weather_risk_score ?? route.features?.weather_risk_score;
          const eventImpact = route.event_impact_score ?? route.features?.event_impact_score;
          const catboostScore = route.catboost_score;
          const landslideStatus = route.landslide_hazard?.blocked
            ? 'BLOCKED'
            : route.features?.landslide_active
              ? route.features?.landslide_severity || 'ACTIVE'
              : 'NONE';

          return (
            <div
              key={idx}
              onClick={() => !isBlocked && onSelect?.(idx)}
              className={`
                relative rounded-xl border transition-all duration-200
                ${isBlocked
                  ? 'bg-rose-950/20 border-rose-800/40 opacity-70 cursor-not-allowed'
                  : isSelected
                    ? 'bg-teal-900/20 border-teal-500/60 cursor-pointer shadow-lg shadow-teal-900/20'
                    : 'bg-slate-900/50 border-slate-800/60 hover:border-slate-700 cursor-pointer hover:bg-slate-900/80'
                }
              `}
            >
              {/* Header */}
              <div className="flex items-start justify-between p-3 pb-2">
                <div className="flex items-center gap-2">
                  <div className={`w-6 h-6 rounded-lg flex items-center justify-center text-[10px] font-bold
                    ${isBlocked ? 'bg-rose-500/20 text-rose-400' : isSelected ? 'bg-teal-500/20 text-teal-300' : 'bg-slate-800 text-slate-400'}`}>
                    {isBlocked ? <Ban className="w-3 h-3" /> : idx + 1}
                  </div>
                  <div>
                    <p className={`text-sm font-bold leading-tight ${isBlocked ? 'line-through text-slate-500' : 'text-slate-100'}`}>
                      {route.name || `Route ${idx + 1}`}
                    </p>
                    {route.blocked_reason && (
                      <p className="text-[10px] text-rose-400 mt-0.5">{route.blocked_reason}</p>
                    )}
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <StatusBadge status={congestionStatus} />
                  {isRecommended && (
                    <span className="flex items-center gap-1 text-[10px] text-teal-400 font-semibold">
                      <CheckCircle2 className="w-3 h-3" />
                      Recommended
                    </span>
                  )}
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="px-3 pb-3 space-y-0">
                <div className="grid grid-cols-2 gap-x-4">
                  <MetricRow label="Distance" value={route.distance_km ? `${route.distance_km}` : null} unit=" km" />
                  <MetricRow label="Duration" value={route.duration_min ? `${Math.round(route.duration_min)}` : null} unit=" min" />
                </div>
                <div className="mt-1 space-y-0 border-t border-slate-800/40 pt-1">
                  <MetricRow
                    label="TCI (Congestion Index)"
                    value={tci != null ? tci.toFixed(2) : null}
                    highlight={tci != null && tci < 1.5}
                  />
                  <MetricRow
                    label="Weather Risk"
                    value={weatherRisk != null ? `${Math.round(weatherRisk * 100)}%` : null}
                  />
                  <MetricRow
                    label="Event Impact"
                    value={eventImpact != null ? `${Math.round(eventImpact * 100)}%` : null}
                  />
                  <MetricRow
                    label="Landslide Status"
                    value={landslideStatus}
                  />
                  {catboostScore != null && (
                    <MetricRow
                      label="CatBoost Score"
                      value={`${Math.round(catboostScore * 100)}%`}
                      highlight={catboostScore > 0.6}
                    />
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
