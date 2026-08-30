/**
 * frontend/src/components/StatCard.jsx
 * Reusable stat card with rich dark/light mode support.
 */
import React from 'react';

export default function StatCard({ title, value, icon: Icon, color = 'indigo', subtitle, onClick }) {
  const colorMap = {
    indigo: 'bg-indigo-100 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 border border-indigo-200/50 dark:border-indigo-800/50',
    emerald: 'bg-emerald-100 dark:bg-emerald-950/70 text-emerald-600 dark:text-emerald-400 border border-emerald-200/50 dark:border-emerald-800/50',
    amber: 'bg-amber-100 dark:bg-amber-950/70 text-amber-600 dark:text-amber-400 border border-amber-200/50 dark:border-amber-800/50',
    rose: 'bg-rose-100 dark:bg-rose-950/70 text-rose-600 dark:text-rose-400 border border-rose-200/50 dark:border-rose-800/50',
    blue: 'bg-blue-100 dark:bg-blue-950/70 text-blue-600 dark:text-blue-400 border border-blue-200/50 dark:border-blue-800/50',
    purple: 'bg-purple-100 dark:bg-purple-950/70 text-purple-600 dark:text-purple-400 border border-purple-200/50 dark:border-purple-800/50',
  };

  return (
    <div
      onClick={onClick}
      className={`bg-white dark:bg-slate-900 rounded-2xl p-5 shadow-sm border border-gray-100 dark:border-slate-800 flex items-center gap-4 hover:shadow-md hover:border-indigo-200 dark:hover:border-slate-700 transition-all ${onClick ? 'cursor-pointer' : ''}`}
    >
      {Icon && (
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${colorMap[color] || colorMap.indigo}`}>
          <Icon className="w-6 h-6" />
        </div>
      )}
      <div className="min-w-0 flex-1">
        <p className="text-sm text-gray-500 dark:text-slate-400 font-medium truncate">{title}</p>
        <p className="text-2xl font-extrabold text-gray-800 dark:text-slate-100 mt-0.5">{value ?? '—'}</p>
        {subtitle && <p className="text-xs text-gray-400 dark:text-slate-500 mt-0.5 truncate">{subtitle}</p>}
      </div>
    </div>
  );
}
