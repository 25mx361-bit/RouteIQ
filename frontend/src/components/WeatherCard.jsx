import React from 'react';
import {
  Cloud,
  CloudRain,
  Sun,
  Wind,
  Droplets,
  Eye,
  Thermometer,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';

export default function WeatherCard({ currentWeather, forecastWeather, loading }) {
  if (loading) {
    return (
      <div className="bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-3 animate-pulse">
        <div className="flex items-center justify-between">
          <div className="h-4 bg-gray-200 dark:bg-slate-800 rounded w-1/3"></div>
          <div className="h-4 bg-gray-200 dark:bg-slate-800 rounded w-1/4"></div>
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div className="h-16 bg-gray-100 dark:bg-slate-800/60 rounded-2xl"></div>
          <div className="h-16 bg-gray-100 dark:bg-slate-800/60 rounded-2xl"></div>
          <div className="h-16 bg-gray-100 dark:bg-slate-800/60 rounded-2xl"></div>
        </div>
      </div>
    );
  }

  const activeWeather = forecastWeather || currentWeather || {
    temperature_2m: 29.5,
    precipitation: 0.0,
    relative_humidity_2m: 58.0,
    wind_speed_10m: 11.2,
    condition: 'Partly Cloudy',
    risk_level: 'Low',
    recommendation: 'Safe driving conditions with clear visibility'
  };

  const {
    temperature_2m = 29.5,
    precipitation = 0.0,
    relative_humidity_2m = 58.0,
    wind_speed_10m = 11.2,
    condition = 'Partly Cloudy',
    risk_level = 'Low',
    recommendation = 'Safe driving conditions with clear visibility',
  } = activeWeather;

  return (
    <div className="bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
      {/* Card Header */}
      <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-sky-100 dark:bg-sky-950 flex items-center justify-center text-sky-600 dark:text-sky-400">
            <Cloud className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-gray-800 dark:text-slate-100">Open-Meteo Weather Corridor</h4>
            <p className="text-[10px] text-gray-400 dark:text-slate-500">{condition} • Coimbatore Region</p>
          </div>
        </div>
        <div className="px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-xs font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>{risk_level} Hazard</span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-gray-50 dark:bg-slate-800/60 rounded-2xl p-3 text-center border border-gray-100 dark:border-slate-800">
          <p className="text-[10px] text-gray-400 dark:text-slate-500 uppercase tracking-wider font-semibold">Temperature</p>
          <p className="text-base font-extrabold text-gray-800 dark:text-slate-100 mt-0.5">{temperature_2m}°<span className="text-[10px] font-normal text-gray-400">C</span></p>
        </div>
        <div className="bg-gray-50 dark:bg-slate-800/60 rounded-2xl p-3 text-center border border-gray-100 dark:border-slate-800">
          <p className="text-[10px] text-gray-400 dark:text-slate-500 uppercase tracking-wider font-semibold">Precipitation</p>
          <p className="text-base font-extrabold text-gray-800 dark:text-slate-100 mt-0.5">{precipitation} <span className="text-[10px] font-normal text-gray-400">mm</span></p>
        </div>
        <div className="bg-gray-50 dark:bg-slate-800/60 rounded-2xl p-3 text-center border border-gray-100 dark:border-slate-800">
          <p className="text-[10px] text-gray-400 dark:text-slate-500 uppercase tracking-wider font-semibold">Wind Velocity</p>
          <p className="text-base font-extrabold text-gray-800 dark:text-slate-100 mt-0.5">{wind_speed_10m} <span className="text-[10px] font-normal text-gray-400">km/h</span></p>
        </div>
      </div>
    </div>
  );
}
