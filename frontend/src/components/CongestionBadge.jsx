/**
 * frontend/src/components/CongestionBadge.jsx
 * Reusable LOW / MEDIUM / HIGH / BLOCKED colored pill with Dark Mode support.
 */
import React from 'react';

const LEVELS = {
  LOW:     { label: 'LOW',     cls: 'bg-emerald-100 dark:bg-emerald-950/70 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800' },
  MEDIUM:  { label: 'MEDIUM',  cls: 'bg-amber-100 dark:bg-amber-950/70 text-amber-700 dark:text-amber-300 border-amber-300 dark:border-amber-800' },
  HIGH:    { label: 'HIGH',    cls: 'bg-orange-100 dark:bg-orange-950/70 text-orange-700 dark:text-orange-300 border-orange-300 dark:border-orange-800' },
  BLOCKED: { label: 'BLOCKED', cls: 'bg-red-100 dark:bg-red-950/70 text-red-700 dark:text-red-300 border-red-300 dark:border-red-800' },
  SAFE:    { label: 'SAFE',    cls: 'bg-emerald-100 dark:bg-emerald-950/70 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800' },
};

export default function CongestionBadge({ level = 'LOW', className = '' }) {
  const cfg = LEVELS[level?.toUpperCase()] || LEVELS.LOW;
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider border ${cfg.cls} ${className}`}>
      {cfg.label}
    </span>
  );
}
