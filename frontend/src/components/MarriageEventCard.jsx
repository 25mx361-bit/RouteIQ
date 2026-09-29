import React from 'react';
import { Heart, MapPin, Users, Car, AlertCircle, Clock } from 'lucide-react';

export default function MarriageEventCard({ event }) {
  if (!event) return null;

  return (
    <div className="relative overflow-hidden bg-white dark:bg-slate-900 border border-rose-200 dark:border-rose-500/30 rounded-2xl p-4 shadow-sm hover:shadow-md transition-all space-y-3">
      <div className="absolute top-0 right-0 w-28 h-28 bg-rose-500/5 rounded-full blur-2xl pointer-events-none"></div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-rose-50 dark:bg-rose-500/20 text-rose-600 dark:text-rose-300 border border-rose-200 dark:border-rose-500/40">
            <Heart className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold tracking-wider text-rose-600 dark:text-rose-400">
              Wedding & Mandapam Gathering
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
              தமிழ் நாட்காட்டி
            </span>
          )}
          <span className="text-[10px] font-semibold px-2.5 py-0.5 rounded-full bg-rose-50 dark:bg-rose-500/20 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-500/40">
            Mandapam Parking Surge
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
      <div className="grid grid-cols-2 gap-2 text-xs bg-rose-50/50 dark:bg-slate-950/80 p-2.5 rounded-xl border border-rose-100 dark:border-rose-500/20">
        <div className="flex items-center gap-1.5 text-gray-700 dark:text-slate-300">
          <MapPin className="w-3.5 h-3.5 text-rose-600 dark:text-rose-400 shrink-0" />
          <span className="truncate">{event.venue_name || 'Kalyana Mandapam'}</span>
        </div>

        <div className="flex items-center gap-1.5 text-gray-700 dark:text-slate-300">
          <Users className="w-3.5 h-3.5 text-rose-600 dark:text-rose-400 shrink-0" />
          <span className="font-semibold">{event.expected_crowd?.toLocaleString() || '3,000+'} Guests</span>
        </div>

        {event.muhurtham_time && (
          <div className="col-span-2 flex items-center gap-1.5 text-amber-700 dark:text-amber-400 pt-1 border-t border-rose-100 dark:border-rose-500/20">
            <Clock className="w-3.5 h-3.5 shrink-0" />
            <span className="font-medium">முகூர்த்த நேரம்: {event.muhurtham_time}</span>
          </div>
        )}
      </div>

      {/* Alert Advisory */}
      <div className="flex items-center gap-2 text-[11px] text-rose-800 dark:text-rose-300/90 bg-rose-50 dark:bg-rose-500/10 p-2.5 rounded-xl border border-rose-200 dark:border-rose-500/20">
        <Car className="w-3.5 h-3.5 text-rose-600 dark:text-rose-400 shrink-0" />
        <span>Mandapam entry/exit parking overflow onto connecting corridor. Slow speeds expected.</span>
      </div>
    </div>
  );
}
