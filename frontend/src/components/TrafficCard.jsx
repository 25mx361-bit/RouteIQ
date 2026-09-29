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

export default function TrafficCard({ trafficData, tci, loading }) {
  if (loading) {
    return (
      <div className="bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-3 animate-pulse">
        <div className="flex items-center justify-between">
          <div className="h-4 bg-gray-200 dark:bg-slate-800 rounded w-1/3"></div>
          <div className="h-4 bg-gray-200 dark:bg-slate-800 rounded w-1/4"></div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="h-16 bg-gray-100 dark:bg-slate-800/60 rounded-2xl"></div>
          <div className="h-16 bg-gray-100 dark:bg-slate-800/60 rounded-2xl"></div>
        </div>
      </div>
    );
  }

  const effectiveTci = tci ?? trafficData?.tci ?? 1.25;
  const currentSpeed = trafficData?.currentSpeed ?? (effectiveTci > 1.8 ? 24 : effectiveTci > 1.4 ? 36 : 46);
  const freeFlowSpeed = trafficData?.freeFlowSpeed ?? 50.0;
  const delayMinutes = trafficData?.delayMinutes ?? (effectiveTci > 1.8 ? 12 : effectiveTci > 1.4 ? 6 : 1);
  const roadStatus = effectiveTci > 2.0 ? 'HEAVY_CONGESTION' : effectiveTci > 1.4 ? 'MODERATE_TRAFFIC' : 'FREE_FLOW';

  const statusConfig = {
    FREE_FLOW: {
      label: 'Free Flow Traffic',
      color: 'text-emerald-600 dark:text-emerald-400',
      bg: 'bg-emerald-50 dark:bg-emerald-950/60 border-emerald-200 dark:border-emerald-800',
      icon: CheckCircle,
    },
    MODERATE_TRAFFIC: {
      label: 'Moderate Flow Delays',
      color: 'text-amber-600 dark:text-amber-400',
      bg: 'bg-amber-50 dark:bg-amber-950/60 border-amber-200 dark:border-amber-800',
      icon: Activity,
    },
    HEAVY_CONGESTION: {
      label: 'Dense Corridor Congestion',
      color: 'text-rose-600 dark:text-rose-400',
      bg: 'bg-rose-50 dark:bg-rose-950/60 border-rose-200 dark:border-rose-800',
      icon: AlertTriangle,
    },
  };

  const currentStatus = statusConfig[roadStatus] || statusConfig.FREE_FLOW;
  const StatusIcon = currentStatus.icon;

  return (
    <div className="bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
      {/* Card Header */}
      <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-indigo-100 dark:bg-indigo-950 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
            <Gauge className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-bold text-gray-800 dark:text-slate-100">TomTom Traffic Dynamics</h4>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                LIVE
              </span>
            </div>
            <p className="text-[10px] text-gray-400 dark:text-slate-500 flex items-center gap-1 mt-0.5">
              <Clock className="w-3 h-3 text-indigo-400" /> Last updated: {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </p>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full border text-xs font-bold flex items-center gap-1.5 ${currentStatus.bg} ${currentStatus.color}`}>
          <StatusIcon className="w-3.5 h-3.5" />
          <span>{currentStatus.label}</span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-gray-50 dark:bg-slate-800/60 rounded-2xl p-3 text-center border border-gray-100 dark:border-slate-800">
          <p className="text-[10px] text-gray-400 dark:text-slate-500 uppercase tracking-wider font-semibold">Speed</p>
          <p className="text-base font-extrabold text-gray-800 dark:text-slate-100 mt-0.5">{currentSpeed} <span className="text-[10px] font-normal text-gray-400">km/h</span></p>
        </div>
        <div className="bg-gray-50 dark:bg-slate-800/60 rounded-2xl p-3 text-center border border-gray-100 dark:border-slate-800">
          <p className="text-[10px] text-gray-400 dark:text-slate-500 uppercase tracking-wider font-semibold">Free Flow</p>
          <p className="text-base font-extrabold text-gray-800 dark:text-slate-100 mt-0.5">{freeFlowSpeed} <span className="text-[10px] font-normal text-gray-400">km/h</span></p>
        </div>
        <div className="bg-gray-50 dark:bg-slate-800/60 rounded-2xl p-3 text-center border border-gray-100 dark:border-slate-800">
          <p className="text-[10px] text-gray-400 dark:text-slate-500 uppercase tracking-wider font-semibold">Est. Delay</p>
          <p className="text-base font-extrabold text-amber-600 dark:text-amber-400 mt-0.5">+{delayMinutes} <span className="text-[10px] font-normal text-gray-400">min</span></p>
        </div>
      </div>
    </div>
  );
}
