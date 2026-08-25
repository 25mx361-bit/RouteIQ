import React from 'react';
import { Flame, MapPin, Users, AlertTriangle, Sparkles, Clock } from 'lucide-react';

export default function FestivalCard({ event }) {
  if (!event) return null;

  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-amber-950/30 via-slate-900 to-slate-900 border border-amber-500/30 rounded-xl p-4 shadow-xl space-y-3">
      <div className="absolute top-0 right-0 w-28 h-28 bg-amber-500/5 rounded-full blur-2xl pointer-events-none"></div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/40">
            <Flame className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold tracking-wider text-amber-400">
              Temple & Cultural Festival
            </div>
            <h4 className="text-xs font-bold text-slate-100">{event.title}</h4>
          </div>
        </div>

        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40">
          Chariot Bottleneck
        </span>
      </div>

      {/* Description */}
      {event.description && (
        <p className="text-xs text-slate-300 leading-relaxed">
          {event.description}
        </p>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-2 gap-2 text-xs bg-slate-950/80 p-2.5 rounded-lg border border-amber-500/20">
        <div className="flex items-center gap-1.5 text-slate-300">
          <MapPin className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span className="truncate">{event.venue_name || event.road_name || 'Town Hall Corridor'}</span>
        </div>

        <div className="flex items-center gap-1.5 text-slate-300">
          <Users className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span className="font-semibold">{event.expected_crowd?.toLocaleString() || '10,000+'} Devotees</span>
        </div>
      </div>

      {/* Alert Advisory */}
      <div className="flex items-center gap-2 text-[11px] text-amber-300/90 bg-amber-500/10 p-2 rounded-lg border border-amber-500/20">
        <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
        <span>Road diversion in place for chariot procession. Expect +15 to +25 mins delay.</span>
      </div>
    </div>
  );
}
