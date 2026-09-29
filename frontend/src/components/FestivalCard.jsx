import React from 'react';
import { Flame, MapPin, Users, AlertTriangle, Sparkles, Clock } from 'lucide-react';

export default function FestivalCard({ event }) {
  if (!event) return null;

  return (
    <div className="relative overflow-hidden bg-white dark:bg-slate-900 border border-amber-200 dark:border-amber-500/30 rounded-2xl p-4 shadow-sm hover:shadow-md transition-all space-y-3">
      <div className="absolute top-0 right-0 w-28 h-28 bg-amber-500/5 rounded-full blur-2xl pointer-events-none"></div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-amber-50 dark:bg-amber-500/20 text-amber-600 dark:text-amber-300 border border-amber-200 dark:border-amber-500/40">
            <Flame className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold tracking-wider text-amber-600 dark:text-amber-400">
              Temple & Cultural Festival
            </div>
            <h4 className="text-sm font-bold text-gray-900 dark:text-slate-100">{event.title}</h4>
            {event.tamil_title && (
              <p className="text-xs font-semibold text-amber-700 dark:text-amber-400 mt-0.5">
                {event.tamil_title}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1.5 flex-wrap justify-end">
          {event.is_tamil_calendar && (
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-700">
              தமிழ் பண்டிகை
            </span>
          )}
          <span className="text-[10px] font-semibold px-2.5 py-0.5 rounded-full bg-amber-50 dark:bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-500/40">
            Chariot Bottleneck
          </span>
        </div>
      </div>

      {/* Description */}
      {event.description && (
        <p className="text-xs text-gray-600 dark:text-slate-300 leading-relaxed">
          {event.description}
        </p>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-2 gap-2 text-xs bg-amber-50/50 dark:bg-slate-950/80 p-2.5 rounded-xl border border-amber-100 dark:border-amber-500/20">
        <div className="flex items-center gap-1.5 text-gray-700 dark:text-slate-300">
          <MapPin className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 shrink-0" />
          <span className="truncate">{event.venue_name || event.road_name || 'Town Hall Corridor'}</span>
        </div>

        <div className="flex items-center gap-1.5 text-gray-700 dark:text-slate-300">
          <Users className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 shrink-0" />
          <span className="font-semibold">{event.expected_crowd?.toLocaleString() || '10,000+'} Devotees</span>
        </div>
      </div>

      {/* Alert Advisory */}
      <div className="flex items-center gap-2 text-[11px] text-amber-800 dark:text-amber-300/90 bg-amber-50 dark:bg-amber-500/10 p-2.5 rounded-xl border border-amber-200 dark:border-amber-500/20">
        <AlertTriangle className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 shrink-0" />
        <span>Road diversion in place for chariot procession. Expect +15 to +25 mins delay.</span>
      </div>
    </div>
  );
}
