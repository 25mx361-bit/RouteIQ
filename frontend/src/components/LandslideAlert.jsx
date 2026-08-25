import React from 'react';
import { AlertOctagon, ShieldAlert, ArrowRight, CheckCircle2, MapPin } from 'lucide-react';

export default function LandslideAlert({ hazard, recommendedRouteName }) {
  if (!hazard) return null;

  return (
    <div className="relative overflow-hidden bg-gradient-to-r from-red-950/80 via-rose-950/60 to-slate-900 border-2 border-red-500/80 rounded-xl p-4 shadow-2xl space-y-3 animate-in fade-in slide-in-from-top-2 duration-300">
      {/* Background Warning Glow */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-red-600/10 rounded-full blur-2xl pointer-events-none"></div>

      {/* Header with Emergency Badge */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-red-600 text-white shadow-lg shadow-red-900/50 animate-bounce">
            <AlertOctagon className="w-5 h-5" />
          </div>
          <div>
            <div className="text-[10px] font-black uppercase tracking-wider text-red-400 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
              Emergency Road Hazard Alert
            </div>
            <h3 className="text-sm font-bold text-white">
              {hazard.title || 'Active Landslide & Rockfall Debris'}
            </h3>
          </div>
        </div>

        <span className="text-[10px] font-mono font-bold px-2.5 py-1 rounded-full bg-red-500/20 text-red-300 border border-red-500/50 uppercase">
          {hazard.severity || 'CRITICAL'} HAZARD
        </span>
      </div>

      {/* Location Details */}
      <div className="grid grid-cols-2 gap-2 text-xs bg-slate-950/90 p-2.5 rounded-lg border border-red-500/30">
        <div className="flex items-center gap-1.5 text-slate-300">
          <MapPin className="w-3.5 h-3.5 text-red-400 shrink-0" />
          <span className="truncate">{hazard.region_name || 'Western Ghats Corridor'}</span>
        </div>
        <div className="flex items-center gap-1.5 text-slate-300">
          <ShieldAlert className="w-3.5 h-3.5 text-red-400 shrink-0" />
          <span className="truncate font-semibold text-red-300">{hazard.road_name || 'Ghat Highway'}</span>
        </div>
      </div>

      {/* Safety Rerouting Notice */}
      <div className="flex items-start gap-2 p-2.5 bg-slate-950/80 rounded-lg border border-emerald-500/30 text-xs">
        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
        <div className="text-slate-300">
          <span className="font-bold text-emerald-300">RouteIQ Safety Rerouting: </span>
          Direct route is <strong className="text-red-400">BLOCKED</strong>. Traffic has been safely rerouted via{' '}
          <strong className="text-emerald-300">{recommendedRouteName || 'Alternative Safe Bypass'}</strong>.
        </div>
      </div>
    </div>
  );
}
