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

/**
 * PredictionChart — shows predicted vs free-flow speed and travel time
 * over a sequence of route segments or time points.
 *
 * Props:
 *   routes   — array of route objects with predicted_speed, free_flow_speed,
 *               predicted_travel_time, free_flow_travel_time, name
 *   title    — optional chart title
 */
export default function PredictionChart({ routes = [], title = 'Route Predictions' }) {
  const data = useMemo(() => {
    if (!routes.length) {
      // Show placeholder trend when no routes yet
      return Array.from({ length: 8 }, (_, i) => ({
        label: `Seg ${i + 1}`,
        predictedSpeed: null,
        freeFlowSpeed: null,
        predictedTime: null,
        freeFlowTime: null,
      }));
    }
    return routes.map((r, idx) => ({
      label: r.name || `Route ${idx + 1}`,
      predictedSpeed: r.predicted_speed ?? r.catboost_score != null
        ? Math.round((r.catboost_score ?? 0.5) * 60)
        : null,
      freeFlowSpeed: r.free_flow_speed ?? 50,
      predictedTime: r.predicted_travel_time != null
        ? Math.round(r.predicted_travel_time / 60)
        : r.duration_min ?? null,
      freeFlowTime: r.free_flow_travel_time != null
        ? Math.round(r.free_flow_travel_time / 60)
        : null,
    }));
  }, [routes]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs shadow-xl">
        <p className="font-bold text-slate-200 mb-1">{label}</p>
        {payload.map((entry) => (
          <div key={entry.dataKey} className="flex items-center gap-2 mb-0.5">
            <span className="w-2 h-2 rounded-full" style={{ background: entry.color }} />
            <span className="text-slate-400">{entry.name}:</span>
            <span className="text-slate-100 font-mono">{entry.value ?? '—'}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 space-y-3">
      <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
        <TrendingUp className="w-4 h-4 text-teal-400" />
        {title}
      </div>

      <div className="space-y-5">
        {/* Speed Chart */}
        <div>
          <p className="text-[11px] text-slate-500 uppercase tracking-wider mb-2">
            Speed Comparison (km/h)
          </p>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={data} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="label" tick={{ fill: '#64748b', fontSize: 10 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ fontSize: 10, color: '#94a3b8' }}
                formatter={(val) => <span style={{ color: '#94a3b8' }}>{val}</span>}
              />
              <Line
                type="monotone"
                dataKey="predictedSpeed"
                name="Predicted Speed"
                stroke="#14b8a6"
                strokeWidth={2}
                dot={{ r: 3, fill: '#14b8a6' }}
                activeDot={{ r: 5 }}
                connectNulls
              />
              <Line
                type="monotone"
                dataKey="freeFlowSpeed"
                name="Free-Flow Speed"
                stroke="#475569"
                strokeWidth={1.5}
                strokeDasharray="4 3"
                dot={false}
                connectNulls
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Travel Time Chart */}
        <div>
          <p className="text-[11px] text-slate-500 uppercase tracking-wider mb-2">
            Travel Time Comparison (min)
          </p>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={data} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="label" tick={{ fill: '#64748b', fontSize: 10 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ fontSize: 10, color: '#94a3b8' }}
                formatter={(val) => <span style={{ color: '#94a3b8' }}>{val}</span>}
              />
              <Line
                type="monotone"
                dataKey="predictedTime"
                name="Predicted Time"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={{ r: 3, fill: '#f59e0b' }}
                activeDot={{ r: 5 }}
                connectNulls
              />
              <Line
                type="monotone"
                dataKey="freeFlowTime"
                name="Free-Flow Time"
                stroke="#475569"
                strokeWidth={1.5}
                strokeDasharray="4 3"
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
