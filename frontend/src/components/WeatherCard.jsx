import React from 'react';
import {
  Cloud,
  CloudRain,
  Sun,
  Wind,
  Droplets,
  Eye,
  Gauge,
  Thermometer,
  ShieldCheck,
  AlertTriangle,
  Sparkles,
} from 'lucide-react';

export default function WeatherCard({
  currentWeather,
  forecastWeather,
  loading,
}) {
  if (loading) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3 animate-pulse">
        <div className="flex items-center justify-between">
          <div className="h-4 bg-slate-800 rounded w-1/3"></div>
          <div className="h-4 bg-slate-800 rounded w-1/4"></div>
        </div>
        <div className="grid grid-cols-3 gap-2">
          <div className="h-14 bg-slate-950 rounded-lg"></div>
          <div className="h-14 bg-slate-950 rounded-lg"></div>
          <div className="h-14 bg-slate-950 rounded-lg"></div>
        </div>
      </div>
    );
  }

  const activeWeather = forecastWeather || currentWeather;
  if (!activeWeather) {
    return null;
  }

  const {
    temperature_2m = 28.0,
    precipitation = 0.0,
    relative_humidity_2m = 65.0,
    wind_speed_10m = 12.0,
    surface_pressure = 1012.0,
    visibility = 10000.0,
    condition = 'Clear sky',
    weather_risk = 0.0,
    risk_level = 'Low',
    risk_factors = ['Optimal conditions'],
    recommendation = 'Safe driving conditions',
  } = activeWeather;

  // Condition Icon Mapping
  const getWeatherIcon = (cond) => {
    const c = (cond || '').toLowerCase();
    if (c.includes('rain') || c.includes('drizzle') || c.includes('shower')) {
      return CloudRain;
    }
    if (c.includes('fog') || c.includes('mist')) {
      return Cloud;
    }
    if (c.includes('wind') || c.includes('storm')) {
      return Wind;
    }
    if (c.includes('cloud') || c.includes('overcast')) {
      return Cloud;
    }
    return Sun;
  };

  const WeatherIcon = getWeatherIcon(condition);

  // Risk styling
  const riskBadgeConfig = {
    Low: {
      bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      bar: 'bg-emerald-500',
    },
    Moderate: {
      bg: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      bar: 'bg-amber-500',
    },
    High: {
      bg: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
      bar: 'bg-rose-500',
    },
    Severe: {
      bg: 'bg-red-500/20 text-red-400 border-red-500/50',
      bar: 'bg-red-500',
    },
  }[risk_level] || {
    bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    bar: 'bg-emerald-500',
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3.5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-teal-500/10 text-teal-400 border border-teal-500/20">
            <WeatherIcon className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-slate-100">
              Atmospheric & Weather Intelligence
            </h3>
            <p className="text-[10px] text-slate-400">
              Open-Meteo Telemetry · {forecastWeather ? 'Target Travel Forecast' : 'Current Conditions'}
            </p>
          </div>
        </div>

        <span
          className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${riskBadgeConfig.bg}`}
        >
          {risk_level} Risk ({Math.round(weather_risk * 100)}%)
        </span>
      </div>

      {/* Weather Condition Highlight Banner */}
      <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-xs">
        <div className="flex items-center gap-2">
          <WeatherIcon className="w-5 h-5 text-teal-400" />
          <div>
            <div className="font-semibold text-slate-200">{condition}</div>
            <div className="text-[10px] text-slate-400">
              {recommendation}
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm font-bold text-slate-100">
            {temperature_2m}°C
          </div>
          <div className="text-[10px] text-slate-500">Air Temp</div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-3 gap-2 text-xs">
        {/* Precipitation */}
        <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/60">
          <div className="flex items-center gap-1 text-[10px] text-slate-500 uppercase">
            <Droplets className="w-3 h-3 text-sky-400" />
            Rainfall
          </div>
          <div className="text-xs font-bold text-slate-200 mt-1">
            {precipitation > 0 ? `${precipitation} mm` : '0.0 mm'}
          </div>
        </div>

        {/* Humidity */}
        <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/60">
          <div className="flex items-center gap-1 text-[10px] text-slate-500 uppercase">
            <Cloud className="w-3 h-3 text-teal-400" />
            Humidity
          </div>
          <div className="text-xs font-bold text-slate-200 mt-1">
            {relative_humidity_2m}%
          </div>
        </div>

        {/* Wind Speed */}
        <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/60">
          <div className="flex items-center gap-1 text-[10px] text-slate-500 uppercase">
            <Wind className="w-3 h-3 text-indigo-400" />
            Wind
          </div>
          <div className="text-xs font-bold text-slate-200 mt-1">
            {wind_speed_10m} <span className="text-[9px] font-normal text-slate-400">km/h</span>
          </div>
        </div>

        {/* Visibility */}
        <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/60">
          <div className="flex items-center gap-1 text-[10px] text-slate-500 uppercase">
            <Eye className="w-3 h-3 text-emerald-400" />
            Visibility
          </div>
          <div className="text-xs font-bold text-slate-200 mt-1">
            {(visibility / 1000).toFixed(1)} <span className="text-[9px] font-normal text-slate-400">km</span>
          </div>
        </div>

        {/* Pressure */}
        <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/60">
          <div className="flex items-center gap-1 text-[10px] text-slate-500 uppercase">
            <Gauge className="w-3 h-3 text-amber-400" />
            Pressure
          </div>
          <div className="text-xs font-bold text-slate-200 mt-1">
            {Math.round(surface_pressure)} <span className="text-[9px] font-normal text-slate-400">hPa</span>
          </div>
        </div>

        {/* Risk Score */}
        <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/60">
          <div className="flex items-center gap-1 text-[10px] text-slate-500 uppercase">
            <ShieldCheck className="w-3 h-3 text-teal-400" />
            Safety Risk
          </div>
          <div className="text-xs font-bold text-slate-200 mt-1">
            {weather_risk.toFixed(2)} / 1.0
          </div>
        </div>
      </div>

      {/* Weather Safety Progress Bar */}
      <div className="space-y-1">
        <div className="flex items-center justify-between text-[10px] text-slate-400">
          <span>Weather Risk Factor</span>
          <span>{Math.round(weather_risk * 100)}%</span>
        </div>
        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${riskBadgeConfig.bar}`}
            style={{ width: `${Math.min(Math.max(weather_risk * 100, 6), 100)}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
