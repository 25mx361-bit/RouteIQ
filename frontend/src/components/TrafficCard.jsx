import React from 'react';
import {
  Gauge,
  Zap,
  Clock,
  AlertTriangle,
  CheckCircle,
  Activity,
  ShieldAlert,
} from 'lucide-react';

export default function TrafficCard({ trafficData, loading }) {
  if (loading) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3 animate-pulse">
        <div className="flex items-center justify-between">
          <div className="h-4 bg-slate-800 rounded w-1/3"></div>
          <div className="h-4 bg-slate-800 rounded w-1/4"></div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="h-14 bg-slate-950 rounded-lg"></div>
          <div className="h-14 bg-slate-950 rounded-lg"></div>
        </div>
      </div>
    );
  }

  if (!trafficData) {
    return null;
  }

  const {
    currentSpeed = 45.0,
    freeFlowSpeed = 50.0,
    delayMinutes = 0.0,
    roadStatus = 'FREE_FLOW',
    confidence = 0.92,
    roadClosure = false,
    speedRatio = 0.9,
  } = trafficData;

  // Status mapping
  const statusConfig = {
    FREE_FLOW: {
      label: 'Free Flow Traffic',
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10 border-emerald-500/30',
      icon: CheckCircle,
    },
    MODERATE_TRAFFIC: {
      label: 'Moderate Delays',
      color: 'text-amber-400',
      bg: 'bg-amber-500/10 border-amber-500/30',
      icon: Activity,
    },
    HEAVY_CONGESTION: {
      label: 'Heavy Congestion',
      color: 'text-rose-400',
      bg: 'bg-rose-500/10 border-rose-500/30',
      icon: AlertTriangle,
    },
    ROAD_CLOSED: {
      label: 'Road Closure / Blocked',
      color: 'text-red-500',
      bg: 'bg-red-500/20 border-red-500/50',
      icon: ShieldAlert,
    },
  }[roadStatus] || {
    label: 'Normal Flow',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10 border-emerald-500/30',
    icon: CheckCircle,
  };

  const StatusIcon = statusConfig.icon;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3.5">
      {/* Header with TomTom source badge */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
            <Gauge className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-slate-100">
              Live Road Traffic Metrics
            </h3>
            <p className="text-[10px] text-slate-400">TomTom Flow Segment API</p>
          </div>
        </div>

        <span className="text-[10px] font-mono px-2 py-0.5 bg-sky-500/10 text-sky-400 border border-sky-500/20 rounded">
          Confidence {Math.round(confidence * 100)}%
        </span>
      </div>

      {/* Road Status Banner */}
      <div
        className={`flex items-center justify-between p-2.5 rounded-lg border text-xs ${statusConfig.bg}`}
      >
        <div className="flex items-center gap-2 font-semibold">
          <StatusIcon className={`w-4 h-4 ${statusConfig.color}`} />
          <span className={statusConfig.color}>{statusConfig.label}</span>
        </div>
        <span className="text-[11px] font-mono text-slate-300">
          {roadClosure ? 'CLOSED' : `${Math.round(speedRatio * 100)}% Flow Ratio`}
        </span>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-3 gap-2 text-xs">
        {/* Current Speed */}
        <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 text-center">
          <div className="text-[10px] text-slate-500 uppercase font-medium">
            Current Speed
          </div>
          <div className="text-sm font-bold text-slate-100 mt-0.5">
            {currentSpeed}{' '}
            <span className="text-[10px] font-normal text-slate-400">km/h</span>
          </div>
        </div>

        {/* Free Flow Speed */}
        <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 text-center">
          <div className="text-[10px] text-slate-500 uppercase font-medium">
            Free-Flow
          </div>
          <div className="text-sm font-bold text-slate-100 mt-0.5">
            {freeFlowSpeed}{' '}
            <span className="text-[10px] font-normal text-slate-400">km/h</span>
          </div>
        </div>

        {/* Delay */}
        <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 text-center">
          <div className="text-[10px] text-slate-500 uppercase font-medium">
            Traffic Delay
          </div>
          <div className="text-sm font-bold text-amber-300 mt-0.5">
            {delayMinutes > 0 ? `+${delayMinutes}m` : '0m'}
          </div>
        </div>
      </div>

      {/* Progress Bar of Traffic Speed Efficiency */}
      <div className="space-y-1">
        <div className="flex items-center justify-between text-[10px] text-slate-400">
          <span>Speed Efficiency</span>
          <span>{currentSpeed} / {freeFlowSpeed} km/h</span>
        </div>
        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${
              speedRatio >= 0.8
                ? 'bg-emerald-500'
                : speedRatio >= 0.5
                ? 'bg-amber-500'
                : 'bg-rose-500'
            }`}
            style={{ width: `${Math.min(Math.max(speedRatio * 100, 5), 100)}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
