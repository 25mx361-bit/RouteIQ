import React from 'react';
import { Heart, MapPin, Users, Car, AlertCircle, Clock } from 'lucide-react';

export default function MarriageEventCard({ event }) {
  if (!event) return null;

  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-rose-950/30 via-slate-900 to-slate-900 border border-rose-500/30 rounded-xl p-4 shadow-xl space-y-3">
      <div className="absolute top-0 right-0 w-28 h-28 bg-rose-500/5 rounded-full blur-2xl pointer-events-none"></div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-rose-500/20 text-rose-300 border border-rose-500/40">
            <Heart className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold tracking-wider text-rose-400">
              Wedding & Mandapam Gathering
            </div>
            <h4 className="text-xs font-bold text-slate-100">{event.title}</h4>
          </div>
        </div>

        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40">
          Mandapam Parking Surge
        </span>
      </div>

      {/* Description */}
      {event.description && (
        <p className="text-xs text-slate-300 leading-relaxed">
          {event.description}
        </p>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-2 gap-2 text-xs bg-slate-950/80 p-2.5 rounded-lg border border-rose-500/20">
        <div className="flex items-center gap-1.5 text-slate-300">
          <MapPin className="w-3.5 h-3.5 text-rose-400 shrink-0" />
          <span className="truncate">{event.venue_name || 'Kalyana Mandapam'}</span>
        </div>

        <div className="flex items-center gap-1.5 text-slate-300">
          <Users className="w-3.5 h-3.5 text-rose-400 shrink-0" />
          <span className="font-semibold">{event.expected_crowd?.toLocaleString() || '3,000+'} Guests</span>
        </div>
      </div>

      {/* Alert Advisory */}
      <div className="flex items-center gap-2 text-[11px] text-rose-300/90 bg-rose-500/10 p-2 rounded-lg border border-rose-500/20">
        <Car className="w-3.5 h-3.5 text-rose-400 shrink-0" />
        <span>Mandapam entry/exit parking overflow onto connecting corridor. Slow speeds expected.</span>
      </div>
    </div>
  );
}
