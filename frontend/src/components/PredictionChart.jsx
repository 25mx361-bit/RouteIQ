import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

export default function PredictionChart({ routes = [], title = 'Route Predictions Telemetry' }) {
  const { isDark } = useTheme();

  const data = useMemo(() => {
    if (!routes || routes.length <= 1) {
      const targetRoute = routes?.[0] || {};
      const targetSpeed = targetRoute.predicted_speed_kmh || 35.0;
      const ffSpeed = targetRoute.free_flow_speed_kmh || 50.0;
      const dist = targetRoute.distance_km || 10.0;
      
      const hours = [
        { label: '06:00', speedFactor: 0.95 },
        { label: '08:00 (Morning Peak)', speedFactor: 0.68 },
        { label: '10:00', speedFactor: 0.82 },
        { label: '12:00', speedFactor: 0.88 },
        { label: '14:00', speedFactor: 0.92 },
        { label: '17:00 (Target Horizon)', speedFactor: 0.58 },
        { label: '19:00', speedFactor: 0.72 },
        { label: '21:00', speedFactor: 0.96 },
      ];

      return hours.map(h => {
        const speed = Math.round(ffSpeed * h.speedFactor);
        const time = Math.round((dist / Math.max(speed, 1)) * 60);
        const idealTime = Math.round((dist / Math.max(ffSpeed, 1)) * 60);
        return {
          label: h.label,
          predictedSpeed: speed,
          freeFlowSpeed: Math.round(ffSpeed),
          predictedTime: time,
          freeFlowTime: idealTime,
        };
      });
    }
    return routes.map((r, idx) => ({
      label: (r.name ? r.name.slice(0, 16) : `Option ${idx + 1}`),
      predictedSpeed: r.predicted_speed_kmh ?? (r.catboost_score != null ? Math.round(r.catboost_score * 50) : 38),
      freeFlowSpeed: r.free_flow_speed_kmh ?? 50,
      predictedTime: r.duration_min ?? (r.predicted_travel_time ? Math.round(r.predicted_travel_time / 60) : 16),
      freeFlowTime: r.free_flow_travel_time ? Math.round(r.free_flow_travel_time / 60) : 12,
    }));
  }, [routes]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-2xl p-3 text-xs shadow-xl">
        <p className="font-bold text-gray-800 dark:text-slate-100 mb-1.5">{label}</p>
        {payload.map((entry) => (
          <div key={entry.dataKey} className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full" style={{ background: entry.color }} />
            <span className="text-gray-500 dark:text-slate-400">{entry.name}:</span>
            <span className="text-gray-900 dark:text-slate-100 font-mono font-semibold">{entry.value ?? '—'}</span>
          </div>
        ))}
      </div>
    );
  };

  const gridColor = isDark ? '#1e293b' : '#e2e8f0';
  const textColor = isDark ? '#64748b' : '#94a3b8';

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Speed Chart */}
        <div className="bg-gray-50/50 dark:bg-slate-950/40 p-4 rounded-2xl border border-gray-100 dark:border-slate-800">
          <p className="text-xs font-semibold text-gray-600 dark:text-slate-400 uppercase tracking-wider mb-3">
            Predicted Speed Dynamics (km/h)
          </p>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
              <XAxis dataKey="label" tick={{ fill: textColor, fontSize: 10 }} />
              <YAxis tick={{ fill: textColor, fontSize: 10 }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Line
                type="monotone"
                dataKey="predictedSpeed"
                name="Predicted Speed"
                stroke="#6366f1"
                strokeWidth={2.5}
                dot={{ r: 3.5, fill: '#6366f1' }}
                activeDot={{ r: 6 }}
                connectNulls
              />
              <Line
                type="monotone"
                dataKey="freeFlowSpeed"
                name="Free-Flow Speed"
                stroke={isDark ? '#475569' : '#94a3b8'}
                strokeWidth={1.5}
                strokeDasharray="4 4"
                dot={false}
                connectNulls
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Travel Time Chart */}
        <div className="bg-gray-50/50 dark:bg-slate-950/40 p-4 rounded-2xl border border-gray-100 dark:border-slate-800">
          <p className="text-xs font-semibold text-gray-600 dark:text-slate-400 uppercase tracking-wider mb-3">
            Expected Duration Progression (min)
          </p>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
              <XAxis dataKey="label" tick={{ fill: textColor, fontSize: 10 }} />
              <YAxis tick={{ fill: textColor, fontSize: 10 }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Line
                type="monotone"
                dataKey="predictedTime"
                name="Predicted Travel Time"
                stroke="#10b981"
                strokeWidth={2.5}
                dot={{ r: 3.5, fill: '#10b981' }}
                activeDot={{ r: 6 }}
                connectNulls
              />
              <Line
                type="monotone"
                dataKey="freeFlowTime"
                name="Ideal Travel Time"
                stroke={isDark ? '#475569' : '#94a3b8'}
                strokeWidth={1.5}
                strokeDasharray="4 4"
                dot={false}
                connectNulls
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
