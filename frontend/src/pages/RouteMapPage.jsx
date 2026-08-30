import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Clock, Navigation, Map as MapIcon, Compass, Sparkles, Layers, CheckCircle } from 'lucide-react';
import MapView from '../components/MapView';
import CongestionBadge from '../components/CongestionBadge';

export default function RouteMapPage() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [selectedRouteIdx, setSelectedRouteIdx] = useState(0);

  useEffect(() => {
    const stored = sessionStorage.getItem('routeiq_search_result');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setData(parsed);
        if (parsed.recommended_route_index !== undefined) {
          setSelectedRouteIdx(parsed.recommended_route_index);
        }
      } catch (e) {}
    }
  }, []);

  if (!data) {
    return (
      <div className="p-8 h-full flex flex-col items-center justify-center bg-gray-50 dark:bg-slate-950 transition-colors">
        <div className="bg-white dark:bg-slate-900 p-8 rounded-3xl shadow-sm border border-gray-100 dark:border-slate-800 text-center max-w-md">
          <MapIcon size={36} className="text-gray-400 dark:text-slate-600 mx-auto mb-3" />
          <h2 className="text-lg font-bold text-gray-800 dark:text-slate-100 mb-2">No Active Route Selected</h2>
          <p className="text-xs text-gray-500 dark:text-slate-400 mb-5">Please initiate a route search to plot the geospatial path.</p>
          <button onClick={() => navigate('/plan')} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-xl text-sm font-semibold transition">
            Go to Plan Route
          </button>
        </div>
      </div>
    );
  }

  const routes = data.routes || [];
  const activeRoute = routes[selectedRouteIdx] || routes[0] || {};
  const tci = activeRoute.tci || 1.2;
  const congestionLevel = activeRoute.congestion_level || (tci > 2 ? 'HIGH' : tci > 1.4 ? 'MEDIUM' : 'LOW');

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col relative bg-slate-950">
      {/* Floating Back Navigation */}
      <div className="absolute top-5 left-5 z-20">
        <button 
          onClick={() => navigate('/recommendations')}
          className="bg-white/95 dark:bg-slate-900/95 backdrop-blur-md text-gray-800 dark:text-slate-100 px-4 py-2.5 rounded-2xl shadow-xl border border-gray-200/50 dark:border-slate-700 hover:bg-white dark:hover:bg-slate-800 flex items-center gap-2 text-xs font-bold transition-all active:scale-95"
        >
          <ArrowLeft size={16} /> 
          <span>Back to Options</span>
        </button>
      </div>

      {/* Floating Summary & Route Switcher Overlay Card */}
      <div className="absolute top-5 right-5 z-20 w-84 max-w-[calc(100vw-2.5rem)] bg-white/95 dark:bg-slate-900/95 backdrop-blur-md rounded-3xl shadow-2xl border border-gray-200/60 dark:border-slate-800 p-4 space-y-3.5">
        <div className="flex items-center justify-between pb-2.5 border-b border-gray-100 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-cyan-100 dark:bg-cyan-950 flex items-center justify-center text-cyan-600 dark:text-cyan-400">
              <Compass size={16} />
            </div>
            <h3 className="font-bold text-gray-800 dark:text-slate-100 text-sm">
              Active Road Path
            </h3>
          </div>
          {activeRoute.is_recommended ? (
            <span className="text-[10px] uppercase px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/70 text-emerald-700 dark:text-emerald-300 font-extrabold flex items-center gap-1">
              <CheckCircle size={10} />
              OPTIMAL
            </span>
          ) : (
            <span className="text-[10px] uppercase px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 font-bold">
              ALTERNATIVE
            </span>
          )}
        </div>
        
        {/* Active Route Details */}
        <div className="space-y-2 text-xs">
          <div className="bg-gray-50 dark:bg-slate-800/60 p-3 rounded-2xl border border-gray-100 dark:border-slate-800">
            <p className="text-[10px] text-gray-400 dark:text-slate-500 uppercase tracking-wider font-semibold">Current Selected Way</p>
            <p className="font-bold text-gray-800 dark:text-cyan-400 text-sm mt-0.5">{activeRoute.name || 'Primary Corridor'}</p>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="bg-gray-50 dark:bg-slate-800/60 p-2.5 rounded-2xl border border-gray-100 dark:border-slate-800">
              <p className="text-[10px] text-gray-400 dark:text-slate-500 uppercase tracking-wider font-semibold">Distance</p>
              <p className="font-bold text-gray-800 dark:text-slate-200 text-sm mt-0.5">
                {activeRoute.distance_km ? `${activeRoute.distance_km.toFixed(1)} km` : `${activeRoute.distance || 0} km`}
              </p>
            </div>
            <div className="bg-gray-50 dark:bg-slate-800/60 p-2.5 rounded-2xl border border-gray-100 dark:border-slate-800">
              <p className="text-[10px] text-gray-400 dark:text-slate-500 uppercase tracking-wider font-semibold">Est. Duration</p>
              <p className="font-bold text-gray-800 dark:text-slate-200 text-sm mt-0.5 flex items-center gap-1">
                <Clock size={13} className="text-cyan-500" />
                {activeRoute.duration_min ? `${Math.round(activeRoute.duration_min)} min` : '14 min'}
              </p>
            </div>
          </div>

          <div className="bg-gray-50 dark:bg-slate-800/60 p-2.5 rounded-2xl border border-gray-100 dark:border-slate-800 flex justify-between items-center">
            <p className="text-[10px] text-gray-400 dark:text-slate-500 uppercase tracking-wider font-semibold">Congestion Index</p>
            <CongestionBadge level={congestionLevel} />
          </div>
        </div>

        {/* 1-Click Alternative Route Selector */}
        {routes.length > 1 && (
          <div className="pt-2 border-t border-gray-100 dark:border-slate-800 space-y-1.5">
            <div className="flex items-center justify-between text-[11px] font-semibold text-slate-400">
              <span className="flex items-center gap-1">
                <Layers size={12} />
                Switch Route Options:
              </span>
            </div>
            <div className="flex flex-col gap-1.5 max-h-36 overflow-y-auto pr-1">
              {routes.map((r, idx) => {
                const isCur = idx === selectedRouteIdx;
                const isBlocked = r.is_blocked || (r.landslide_hazard && r.landslide_hazard.blocked);

                return (
                  <button
                    key={`route-tab-${idx}`}
                    onClick={() => setSelectedRouteIdx(idx)}
                    className={`w-full text-left p-2 rounded-xl transition-all flex items-center justify-between text-xs border ${
                      isCur
                        ? 'bg-cyan-500/15 border-cyan-500/60 text-cyan-300 font-bold shadow-sm'
                        : isBlocked
                        ? 'bg-red-500/10 border-red-500/30 text-red-400 opacity-70'
                        : 'bg-slate-800/40 border-slate-700/50 text-slate-300 hover:bg-slate-800'
                    }`}
                  >
                    <div className="truncate mr-2">
                      <div className="truncate text-[11px]">
                        {r.name || `Route ${idx + 1}`}
                      </div>
                      <div className="text-[10px] text-slate-400 font-normal">
                        {r.distance_km} km · {Math.round(r.duration_min)} min
                      </div>
                    </div>
                    {isCur ? (
                      <span className="shrink-0 w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                    ) : isBlocked ? (
                      <span className="shrink-0 text-[9px] px-1 bg-red-500/20 text-red-300 rounded font-bold">BLOCKED</span>
                    ) : (
                      <span className="shrink-0 text-[10px] text-slate-400">Select</span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Map Component */}
      <div className="flex-1 w-full h-full">
        <MapView 
          sourceCoords={data.source}
          destCoords={data.destination}
          routes={routes} 
          selectedRoute={selectedRouteIdx}
          onSelectRoute={setSelectedRouteIdx}
        />
      </div>
    </div>
  );
}
