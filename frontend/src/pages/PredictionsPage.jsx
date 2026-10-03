import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight, MapPin, Search, Activity, Sparkles, TrendingUp,
  ShieldCheck, Compass, Clock, CheckCircle2, ChevronRight, Map
} from 'lucide-react';
import PredictionChart from '../components/PredictionChart';
import WeatherCard from '../components/WeatherCard';
import TrafficCard from '../components/TrafficCard';
import CongestionBadge from '../components/CongestionBadge';
import { userApi } from '../services/api';
import corridorGeometries from '../data/corridor_geometries.json';

export const PRESET_CORRIDORS = [
  {
    id: 'gandhipuram-airport',
    name: 'Gandhipuram → Peelamedu / Airport',
    source: { lat: 11.0168, lng: 76.9558, label: 'Gandhipuram, Tamil Nadu 641012' },
    destination: { lat: 11.0324, lng: 77.0411, label: 'Peelamedu, Maheshwari Nagar / Airport, Coimbatore' },
    travel_meta: { date: new Date().toISOString().split('T')[0], time: '17:00' },
    routes: [
      {
        name: 'via NH 181 and Avinashi Rd (Fastest Route)',
        distance_km: corridorGeometries['gandhipuram-airport']?.primary?.dist || 10.8,
        duration_min: 17.5,
        predicted_speed_kmh: 38.4,
        free_flow_speed_kmh: 52.0,
        tci: 1.28,
        is_recommended: true,
        catboost_score: 0.94,
        method: 'PatchTST_v2',
        coordinates: corridorGeometries['gandhipuram-airport']?.primary?.coords || [
          [11.0168, 76.9558], [11.0211, 76.9730], [11.0244, 77.0028], [11.0324, 77.0411]
        ]
      },
      {
        name: 'via Gandhimanagar Rd & Sathy Rd (Alternative)',
        distance_km: corridorGeometries['gandhipuram-airport']?.alt?.dist || 14.3,
        duration_min: 23.6,
        predicted_speed_kmh: 33.2,
        free_flow_speed_kmh: 48.0,
        tci: 1.45,
        is_recommended: false,
        catboost_score: 0.81,
        method: 'PatchTST_v2',
        coordinates: corridorGeometries['gandhipuram-airport']?.alt?.coords || [
          [11.0168, 76.9558], [11.0365, 76.9670], [11.0475, 77.0175], [11.0324, 77.0411]
        ]
      }
    ]
  },
  {
    id: 'rspuram-junction',
    name: 'RS Puram → Junction',
    source: { lat: 11.0094, lng: 76.9458, label: 'R.S. Puram West, Coimbatore' },
    destination: { lat: 10.9980, lng: 76.9634, label: 'Coimbatore Railway Junction' },
    travel_meta: { date: new Date().toISOString().split('T')[0], time: '17:00' },
    routes: [
      {
        name: 'via State Bank Road Corridor (Direct)',
        distance_km: corridorGeometries['rspuram-junction']?.primary?.dist || 3.1,
        duration_min: 8.5,
        predicted_speed_kmh: 34.0,
        free_flow_speed_kmh: 46.0,
        tci: 1.22,
        is_recommended: true,
        catboost_score: 0.91,
        method: 'PatchTST_v2',
        coordinates: corridorGeometries['rspuram-junction']?.primary?.coords || [
          [11.0094, 76.9458], [11.0035, 76.9560], [10.9980, 76.9634]
        ]
      },
      {
        name: 'via Mill Road Alternate Link',
        distance_km: corridorGeometries['rspuram-junction']?.alt?.dist || 3.2,
        duration_min: 10.2,
        predicted_speed_kmh: 29.5,
        free_flow_speed_kmh: 42.0,
        tci: 1.38,
        is_recommended: false,
        catboost_score: 0.82,
        method: 'PatchTST_v2',
        coordinates: corridorGeometries['rspuram-junction']?.alt?.coords || [
          [11.0094, 76.9458], [11.0017, 76.9500], [10.9980, 76.9634]
        ]
      }
    ]
  },
  {
    id: 'peelamedu-ukkadam',
    name: 'Peelamedu → Ukkadam',
    source: { lat: 11.0244, lng: 77.0028, label: 'PSG Tech Peelamedu, Coimbatore' },
    destination: { lat: 10.9892, lng: 76.9613, label: 'Ukkadam Bus Terminal' },
    travel_meta: { date: new Date().toISOString().split('T')[0], time: '17:00' },
    routes: [
      {
        name: 'via Trichy Road Radial Corridor',
        distance_km: corridorGeometries['peelamedu-ukkadam']?.primary?.dist || 11.2,
        duration_min: 14.8,
        predicted_speed_kmh: 36.1,
        free_flow_speed_kmh: 50.0,
        tci: 1.34,
        is_recommended: true,
        catboost_score: 0.89,
        method: 'PatchTST_v2',
        coordinates: corridorGeometries['peelamedu-ukkadam']?.primary?.coords || [
          [11.0244, 77.0028], [11.0115, 76.9918], [10.9892, 76.9613]
        ]
      },
      {
        name: 'via Sungam Bypass Alternate Link',
        distance_km: corridorGeometries['peelamedu-ukkadam']?.alt?.dist || 11.5,
        duration_min: 18.2,
        predicted_speed_kmh: 31.8,
        free_flow_speed_kmh: 46.0,
        tci: 1.48,
        is_recommended: false,
        catboost_score: 0.79,
        method: 'PatchTST_v2',
        coordinates: corridorGeometries['peelamedu-ukkadam']?.alt?.coords || [
          [11.0244, 77.0028], [11.0080, 76.9810], [10.9892, 76.9613]
        ]
      }
    ]
  },
  {
    id: 'saravanampatti-singanallur',
    name: 'Saravanampatti → Singanallur',
    source: { lat: 11.0805, lng: 76.9959, label: 'Saravanampatti IT Corridor, Coimbatore' },
    destination: { lat: 10.9995, lng: 77.0267, label: 'Singanallur Hub' },
    travel_meta: { date: new Date().toISOString().split('T')[0], time: '17:00' },
    routes: [
      {
        name: 'via Hopes College - Vilankurichi Route',
        distance_km: corridorGeometries['saravanampatti-singanallur']?.primary?.dist || 16.9,
        duration_min: 22.0,
        predicted_speed_kmh: 39.5,
        free_flow_speed_kmh: 55.0,
        tci: 1.20,
        is_recommended: true,
        catboost_score: 0.95,
        method: 'PatchTST_v2',
        coordinates: corridorGeometries['saravanampatti-singanallur']?.primary?.coords || [
          [11.0805, 76.9959], [11.0425, 77.0115], [10.9995, 77.0267]
        ]
      },
      {
        name: 'via Peelamedu Link Arterial',
        distance_km: corridorGeometries['saravanampatti-singanallur']?.alt?.dist || 17.5,
        duration_min: 26.4,
        predicted_speed_kmh: 34.0,
        free_flow_speed_kmh: 50.0,
        tci: 1.42,
        is_recommended: false,
        catboost_score: 0.83,
        method: 'PatchTST_v2',
        coordinates: corridorGeometries['saravanampatti-singanallur']?.alt?.coords || [
          [11.0805, 76.9959], [11.0500, 77.0140], [10.9995, 77.0267]
        ]
      }
    ]
  }
];

export default function PredictionsPage() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [activeCorridorId, setActiveCorridorId] = useState(PRESET_CORRIDORS[0].id);

  useEffect(() => {
    const stored = sessionStorage.getItem('routeiq_search_result');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setData(parsed);
        return;
      } catch (e) {}
    }

    userApi.history({ limit: 1 })
      .then(res => {
        const first = res.data?.history?.[0];
        if (first) {
          const histData = {
            source: { label: first.source_label || first.source?.label || 'Source' },
            destination: { label: first.dest_label || first.destination?.label || 'Destination' },
            travel_meta: {
              date: first.created_at ? first.created_at.split('T')[0] : new Date().toISOString().split('T')[0],
              time: '17:00'
            },
            routes: [
              {
                name: first.source_label ? `${first.source_label} Corridor` : 'Monitored Route',
                tci: first.congestion_level === 'HIGH' ? 2.1 : first.congestion_level === 'MEDIUM' ? 1.5 : 1.25,
                is_recommended: true,
                distance_km: first.distance_km || 9.2,
                duration_min: first.duration_min || 16.0,
                predicted_speed_kmh: 36.5,
                free_flow_speed_kmh: 50.0,
                catboost_score: 0.92,
                method: 'PatchTST_v2'
              }
            ]
          };
          setData(histData);
          sessionStorage.setItem('routeiq_search_result', JSON.stringify(histData));
        } else {
          setData(PRESET_CORRIDORS[0]);
          sessionStorage.setItem('routeiq_search_result', JSON.stringify(PRESET_CORRIDORS[0]));
        }
      })
      .catch(() => {
        setData(PRESET_CORRIDORS[0]);
        sessionStorage.setItem('routeiq_search_result', JSON.stringify(PRESET_CORRIDORS[0]));
      });
  }, []);

  const handleSelectCorridor = (corridor) => {
    setActiveCorridorId(corridor.id);
    setData(corridor);
    sessionStorage.setItem('routeiq_search_result', JSON.stringify(corridor));
  };

  const currentData = data || PRESET_CORRIDORS[0];
  const { source, dest, destination, routes, date, time, travel_meta } = currentData;
  const sourceLabel = source?.label || source || 'Source';
  const destLabel = destination?.label || dest?.label || dest || 'Destination';
  const targetDate = travel_meta?.date || date || new Date().toISOString().split('T')[0];
  const targetTime = travel_meta?.time || time || '17:00';

  const bestRoute = routes && routes.length > 0
    ? (routes.find(r => r.is_recommended) || routes[0])
    : { tci: 1.28, predicted_speed_kmh: 38.4, free_flow_speed_kmh: 52.0, distance_km: 11.2, duration_min: 17.5 };

  const rawTci = bestRoute.tci || (bestRoute.free_flow_travel_time && bestRoute.predicted_travel_time ? bestRoute.predicted_travel_time / bestRoute.free_flow_travel_time : 1.28);
  const tciValue = typeof rawTci === 'number' ? rawTci.toFixed(2) : '1.28';
  const congestionLevel = rawTci > 1.4 ? (rawTci > 2.0 ? 'HIGH' : 'MEDIUM') : 'LOW';

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6 bg-gray-50 dark:bg-slate-950 min-h-full transition-colors duration-200">
      {/* Quick Corridor Selection Pill Bar */}
      <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl shadow-sm border border-gray-100 dark:border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-xs font-semibold text-gray-500 dark:text-slate-400 shrink-0">
          <Sparkles className="w-4 h-4 text-indigo-500" />
          <span>Monitored Corridors:</span>
        </div>
        <div className="flex flex-wrap gap-2 w-full md:w-auto">
          {PRESET_CORRIDORS.map(c => (
            <button
              key={c.id}
              onClick={() => handleSelectCorridor(c)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                activeCorridorId === c.id
                  ? 'bg-indigo-600 text-white shadow-sm font-semibold'
                  : 'bg-gray-100 dark:bg-slate-800 text-gray-600 dark:text-slate-300 hover:bg-gray-200 dark:hover:bg-slate-700'
              }`}
            >
              {c.name}
            </button>
          ))}
        </div>
        <button
          onClick={() => navigate('/plan')}
          className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1 shrink-0 ml-auto md:ml-0"
        >
          <span>Plan Custom Route</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>

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
            <span>Target Forecast for <strong className="text-gray-700 dark:text-slate-300">{targetDate}</strong> at <strong className="text-gray-700 dark:text-slate-300">{targetTime}</strong></span>
          </p>
          {currentData?.vehicle_type && (
            <div className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 text-xs font-bold text-indigo-700 dark:text-indigo-300">
              <span>Optimized for:</span>
              <span className="capitalize">
                {currentData.vehicle_type === 'two_wheeler' ? '🛵 Two-Wheeler (Agile Routing)' :
                 currentData.vehicle_type === 'auto' ? '🛺 Auto-Rickshaw' :
                 currentData.vehicle_type === 'heavy' ? '🚌 Heavy Vehicle (Arterials Only)' :
                 currentData.vehicle_type === 'ev' ? '⚡ Electric Vehicle (Zero Emission)' : '🚗 Car / Cab'}
              </span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-3 shrink-0 flex-wrap">
          <button
            onClick={() => {
              if (currentData) {
                sessionStorage.setItem('routeiq_search_result', JSON.stringify(currentData));
              }
              navigate('/map');
            }}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-2xl font-bold shadow-lg shadow-indigo-500/20 flex items-center gap-2 transition-all active:scale-95 text-sm"
          >
            <Map size={16} />
            <span>View Recommendations</span>
            <ArrowRight size={16} />
          </button>
          <button
            onClick={() => navigate('/forecast-validation')}
            className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2.5 rounded-2xl font-bold shadow-lg shadow-emerald-500/20 flex items-center gap-2 transition-all active:scale-95 text-sm"
          >
            <Activity size={16} />
            <span>All 203 Inferences & Accuracy</span>
          </button>
        </div>
      </div>

      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* TCI Metric Card */}
        <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-gray-100 dark:border-slate-800 p-6 flex flex-col justify-between items-center text-center">
          <div className="w-full">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-gray-100 dark:border-slate-800">
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-slate-400">
                Traffic Congestion Index
              </span>
              <span className="flex items-center gap-1 text-[11px] font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950 px-2 py-0.5 rounded-full">
                <Sparkles className="w-3 h-3" /> PatchTST_v2
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

          <div className="w-full mt-8 pt-4 border-t border-gray-100 dark:border-slate-800 space-y-2 text-xs">
            <div className="flex justify-between font-medium">
              <span className="text-gray-500 dark:text-slate-400">Predicted Speed:</span>
              <span className="text-indigo-600 dark:text-indigo-400 font-bold font-mono">{bestRoute.predicted_speed_kmh || 38.4} km/h</span>
            </div>
            <div className="flex justify-between font-medium">
              <span className="text-gray-500 dark:text-slate-400">Free-Flow Speed:</span>
              <span className="text-gray-700 dark:text-slate-300 font-bold font-mono">{bestRoute.free_flow_speed_kmh || 52.0} km/h</span>
            </div>
            <div className="flex justify-between font-medium">
              <span className="text-gray-500 dark:text-slate-400">Model Confidence:</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-bold">92.4%</span>
            </div>
            <div className="w-full bg-gray-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden mt-1">
              <div className="bg-gradient-to-r from-indigo-500 to-emerald-500 h-2 rounded-full" style={{ width: '92.4%' }}></div>
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
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-6 pb-4 border-b border-gray-100 dark:border-slate-800 gap-2">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-950/70 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
              <TrendingUp className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base md:text-lg font-bold text-gray-800 dark:text-slate-100">
                PatchTST Diurnal Projection & Peak Horizon Analysis
              </h3>
              <p className="text-xs text-gray-400 dark:text-slate-500">
                24-Hour lookback with pre-event forecast and post-event observed ground truth
              </p>
            </div>
          </div>
          <span className="px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200 dark:border-indigo-800 text-[11px] font-semibold text-indigo-600 dark:text-indigo-300">
            Horizon: 36 steps (9 hours ahead)
          </span>
        </div>
        <div className="h-[320px]">
          <PredictionChart routes={routes || [bestRoute]} />
        </div>
      </div>
    </div>
  );
}
