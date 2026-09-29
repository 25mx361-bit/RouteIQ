import React from 'react';
import { AlertOctagon, ShieldAlert, ArrowRight, CheckCircle2, MapPin } from 'lucide-react';

export default function LandslideAlert({ hazard, recommendedRouteName }) {
  if (!hazard) return null;

  return (
    <div className="relative overflow-hidden bg-gradient-to-r from-red-600 via-rose-600 to-rose-700 dark:from-red-950/90 dark:via-rose-950/80 dark:to-slate-900 border-2 border-red-500 rounded-2xl p-4 shadow-xl space-y-3 animate-in fade-in slide-in-from-top-2 duration-300 text-white">
      {/* Background Warning Glow */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 dark:bg-red-600/10 rounded-full blur-2xl pointer-events-none"></div>

      {/* Header with Emergency Badge */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-xl bg-white/20 backdrop-blur-sm text-white shadow-md animate-bounce">
            <AlertOctagon className="w-5 h-5" />
          </div>
          <div>
            <div className="text-[10px] font-black uppercase tracking-wider text-red-100 dark:text-red-400 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-white dark:bg-red-500 animate-ping"></span>
              Emergency Road Hazard Alert
            </div>
            <h3 className="text-sm font-bold text-white">
              {hazard.title || 'Active Landslide & Rockfall Debris'}
            </h3>
          </div>
        </div>

        <span className="text-[10px] font-mono font-bold px-2.5 py-1 rounded-full bg-white/20 dark:bg-red-500/20 text-white dark:text-red-300 border border-white/30 dark:border-red-500/50 uppercase">
          {hazard.severity || 'CRITICAL'} HAZARD
        </span>
      </div>

      {/* Location Details */}
      <div className="grid grid-cols-2 gap-2 text-xs bg-black/25 backdrop-blur-sm p-2.5 rounded-xl border border-white/15 dark:border-red-500/30">
        <div className="flex items-center gap-1.5 text-white/90 dark:text-slate-300">
          <MapPin className="w-3.5 h-3.5 text-amber-300 dark:text-red-400 shrink-0" />
          <span className="truncate">{hazard.region_name || 'Western Ghats Corridor'}</span>
        </div>
        <div className="flex items-center gap-1.5 text-white/90 dark:text-slate-300">
          <ShieldAlert className="w-3.5 h-3.5 text-amber-300 dark:text-red-400 shrink-0" />
          <span className="truncate font-semibold text-white dark:text-red-300">{hazard.road_name || 'Ghat Highway'}</span>
        </div>
      </div>

      {/* Safety Rerouting Notice */}
      <div className="flex items-start gap-2 p-2.5 bg-black/25 backdrop-blur-sm rounded-xl border border-emerald-400/40 dark:border-emerald-500/30 text-xs">
        <CheckCircle2 className="w-4 h-4 text-emerald-300 dark:text-emerald-400 shrink-0 mt-0.5" />
        <div className="text-white/95 dark:text-slate-300">
          <span className="font-bold text-emerald-200 dark:text-emerald-300">RouteIQ Safety Rerouting: </span>
          Direct route is <strong className="underline decoration-white/60 dark:text-red-400">BLOCKED</strong>. Traffic has been safely rerouted via{' '}
          <strong className="text-emerald-200 dark:text-emerald-300">{recommendedRouteName || 'Alternative Safe Bypass'}</strong>.
        </div>
      </div>
    </div>
  );
}
