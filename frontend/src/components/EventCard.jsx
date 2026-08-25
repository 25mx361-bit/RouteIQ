import React from 'react';
import {
  Calendar,
  MapPin,
  Users,
  AlertTriangle,
  Sparkles,
  Flame,
  Heart,
  Trophy,
  GraduationCap,
  Megaphone,
} from 'lucide-react';

export const EVENT_TYPE_CONFIG = {
  FESTIVAL: {
    label: 'Festival & Temple Procession',
    icon: Flame,
    color: 'text-amber-400',
    bg: 'bg-amber-500/10 border-amber-500/30',
  },
  MARRIAGE: {
    label: 'Marriage & Reception',
    icon: Heart,
    color: 'text-rose-400',
    bg: 'bg-rose-500/10 border-rose-500/30',
  },
  SPORTS_EVENT: {
    label: 'Sports & Marathon',
    icon: Trophy,
    color: 'text-blue-400',
    bg: 'bg-blue-500/10 border-blue-500/30',
  },
  POLITICAL_EVENT: {
    label: 'Political Rally / VIP',
    icon: Megaphone,
    color: 'text-purple-400',
    bg: 'bg-purple-500/10 border-purple-500/30',
  },
  COLLEGE_EVENT: {
    label: 'College Symposium',
    icon: GraduationCap,
    color: 'text-teal-400',
    bg: 'bg-teal-500/10 border-teal-500/30',
  },
  SCHOOL_EVENT: {
    label: 'School Function',
    icon: GraduationCap,
    color: 'text-sky-400',
    bg: 'bg-sky-500/10 border-sky-500/30',
  },
  PUBLIC_EVENT: {
    label: 'Public Gathering',
    icon: Users,
    color: 'text-indigo-400',
    bg: 'bg-indigo-500/10 border-indigo-500/30',
  },
  OTHER: {
    label: 'Road Event / Gathering',
    icon: AlertTriangle,
    color: 'text-slate-400',
    bg: 'bg-slate-500/10 border-slate-500/30',
  },
};

export const IMPACT_LEVEL_CONFIG = {
  CRITICAL: {
    label: 'Critical Bottleneck',
    badge: 'bg-red-500/20 text-red-400 border-red-500/40',
  },
  HIGH: {
    label: 'High Impact',
    badge: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
  },
  MEDIUM: {
    label: 'Medium Delay',
    badge: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  },
  LOW: {
    label: 'Low Impact',
    badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  },
};

export default function EventCard({ event, onEdit, onDelete, isAdmin = false }) {
  if (!event) return null;

  const typeConfig = EVENT_TYPE_CONFIG[event.event_type] || EVENT_TYPE_CONFIG.OTHER;
  const impactConfig = IMPACT_LEVEL_CONFIG[event.impact_level] || IMPACT_LEVEL_CONFIG.MEDIUM;
  const TypeIcon = typeConfig.icon;

  const formatDate = (d) => {
    if (!d) return 'Ongoing';
    try {
      return new Date(d).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return d;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg hover:border-slate-700 transition-all space-y-3">
      {/* Top Badges */}
      <div className="flex items-center justify-between gap-2">
        <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-semibold ${typeConfig.bg}`}>
          <TypeIcon className={`w-3.5 h-3.5 ${typeConfig.color}`} />
          <span className={typeConfig.color}>{typeConfig.label}</span>
        </div>

        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${impactConfig.badge}`}>
          {impactConfig.label}
        </span>
      </div>

      {/* Title & Description */}
      <div>
        <h4 className="text-sm font-bold text-slate-100">{event.title}</h4>
        {event.description && (
          <p className="text-xs text-slate-400 mt-1 line-clamp-2">{event.description}</p>
        )}
      </div>

      {/* Location & Crowd Metrics */}
      <div className="grid grid-cols-2 gap-2 text-xs bg-slate-950/80 p-2.5 rounded-lg border border-slate-800/80">
        <div className="flex items-center gap-1.5 text-slate-300">
          <MapPin className="w-3.5 h-3.5 text-teal-400 shrink-0" />
          <span className="truncate">{event.venue_name || event.road_name || 'Coimbatore Venue'}</span>
        </div>

        <div className="flex items-center gap-1.5 text-slate-300">
          <Users className="w-3.5 h-3.5 text-blue-400 shrink-0" />
          <span>{event.expected_crowd?.toLocaleString() || 500} expected</span>
        </div>
      </div>

      {/* Timing & Admin Actions */}
      <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
        <div className="flex items-center gap-1">
          <Calendar className="w-3.5 h-3.5 text-slate-500" />
          <span>{formatDate(event.start_time)}</span>
        </div>

        {isAdmin && (
          <div className="flex items-center gap-2">
            {onEdit && (
              <button
                onClick={() => onEdit(event)}
                className="text-blue-400 hover:text-blue-300 font-medium cursor-pointer"
              >
                Edit
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => onDelete(event._id)}
                className="text-rose-400 hover:text-rose-300 font-medium cursor-pointer"
              >
                Delete
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
