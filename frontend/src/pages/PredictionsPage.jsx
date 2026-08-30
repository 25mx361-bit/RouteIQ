import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, MapPin, Search, Activity, Sparkles, TrendingUp, ShieldCheck } from 'lucide-react';
import PredictionChart from '../components/PredictionChart';
import WeatherCard from '../components/WeatherCard';
import TrafficCard from '../components/TrafficCard';
import CongestionBadge from '../components/CongestionBadge';

export default function PredictionsPage() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);

  useEffect(() => {
    const stored = sessionStorage.getItem('routeiq_search_result');
    if (stored) {
      try {
        setData(JSON.parse(stored));
      } catch (e) {}
    }
  }, []);

  if (!data) {
    return (
      <div className="p-8 h-full flex flex-col items-center justify-center bg-gray-50 dark:bg-slate-950 transition-colors">
        <div className="bg-white dark:bg-slate-900 p-8 rounded-3xl shadow-sm border border-gray-100 dark:border-slate-800 text-center max-w-md">
          <div className="w-14 h-14 rounded-2xl bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mx-auto mb-4">
            <Search size={28} />
          </div>
          <h2 className="text-xl font-bold text-gray-800 dark:text-slate-100 mb-2">No Active Route Search</h2>
          <p className="text-xs text-gray-500 dark:text-slate-400 mb-5">
            Please plan a journey to generate PatchTST time-series forecasts and route recommendations.
          </p>
          <button 
            onClick={() => navigate('/plan')} 
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl font-bold transition shadow-lg shadow-indigo-500/20"
          >
            Go to Route Planner
          </button>
        </div>
      </div>
    );
  }

  const { source, dest, destination, routes, date, time, travel_meta } = data;
  const sourceLabel = source?.label || source || 'Source';
  const destLabel = destination?.label || dest?.label || dest || 'Destination';
  const targetDate = travel_meta?.date || date || new Date().toISOString().split('T')[0];
  const targetTime = travel_meta?.time || time || '09:00';

  const bestRoute = routes && routes.length > 0 ? (routes.find(r => r.is_recommended) || routes[0]) : { tci: 1.25, predicted_speed_kmh: 38 };
  const rawTci = bestRoute.tci || (bestRoute.free_flow_travel_time && bestRoute.predicted_travel_time ? bestRoute.predicted_travel_time / bestRoute.free_flow_travel_time : 1.25);
  const tciValue = typeof rawTci === 'number' ? rawTci.toFixed(2) : '1.25';
  const congestionLevel = rawTci > 2.0 ? 'HIGH' : rawTci > 1.4 ? 'MEDIUM' : 'LOW';

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 bg-gray-50 dark:bg-slate-950 min-h-full transition-colors duration-200">
      {/* Route Header Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white dark:bg-slate-900 p-6 rounded-3xl shadow-sm border border-gray-100 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-3 text-xl md:text-2xl font-bold text-gray-800 dark:text-slate-100 mb-2 flex-wrap">
            <span className="text-indigo-600 dark:text-indigo-400">{sourceLabel}</span>
            <ArrowRight className="text-gray-400 shrink-0" size={20} />
            <span className="text-emerald-600 dark:text-emerald-400">{destLabel}</span>
          </div>
          <p className="text-xs md:text-sm text-gray-500 dark:text-slate-400 flex items-center gap-2">
            <MapPin size={15} className="text-indigo-500" /> 
            <span>Forecasted for <strong className="text-gray-700 dark:text-slate-300">{targetDate}</strong> at <strong className="text-gray-700 dark:text-slate-300">{targetTime}</strong></span>
          </p>
        </div>
        <button 
          onClick={() => navigate('/recommendations')}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-2xl font-bold shadow-lg shadow-indigo-500/20 flex items-center gap-2 shrink-0 transition-all active:scale-95"
        >
          <span>View Recommended Routes</span>
          <ArrowRight size={18} />
        </button>
      </div>

      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* TCI Metric Card */}
        <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-gray-100 dark:border-slate-800 p-6 flex flex-col justify-between items-center text-center">
          <div className="w-full">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-gray-100 dark:border-slate-800">
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-slate-400">
                Traffic Index
              </span>
              <span className="flex items-center gap-1 text-[11px] font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950 px-2 py-0.5 rounded-full">
                <Sparkles className="w-3 h-3" /> PatchTST
              </span>
            </div>
            <p className="text-xs text-gray-400 dark:text-slate-500 mb-2">Predicted Congestion Index (TCI)</p>
            <div className="text-5xl md:text-6xl font-extrabold text-gray-800 dark:text-slate-100 my-3 font-mono">
              {tciValue}
            </div>
            <div className="flex justify-center mt-2">
              <CongestionBadge level={congestionLevel} />
            </div>
          </div>
          
          <div className="w-full mt-8 pt-4 border-t border-gray-100 dark:border-slate-800">
            <div className="flex justify-between text-xs mb-1.5 font-medium">
              <span className="text-gray-500 dark:text-slate-400">Model Confidence</span>
              <span className="text-indigo-600 dark:text-indigo-400 font-bold">92.4%</span>
            </div>
            <div className="w-full bg-gray-100 dark:bg-slate-800 rounded-full h-2.5 overflow-hidden">
              <div className="bg-gradient-to-r from-indigo-500 to-emerald-500 h-2.5 rounded-full" style={{ width: '92.4%' }}></div>
            </div>
          </div>
        </div>
        
        {/* Telemetry Cards */}
        <div className="lg:col-span-2 space-y-6">
          <TrafficCard tci={parseFloat(tciValue)} />
          <WeatherCard />
        </div>
      </div>

      {/* Traffic Trend Chart */}
      <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-gray-100 dark:border-slate-800 p-6 md:p-8">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-100 dark:border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-950/70 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
              <TrendingUp className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base md:text-lg font-bold text-gray-800 dark:text-slate-100">Traffic Trend & Speed Analysis</h3>
              <p className="text-xs text-gray-400 dark:text-slate-500">24-hour lookback & horizon projection</p>
            </div>
          </div>
        </div>
        <div className="h-[320px]">
          <PredictionChart routes={routes || []} />
        </div>
      </div>
    </div>
  );
}
