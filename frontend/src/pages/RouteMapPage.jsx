import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Clock, Navigation, Map as MapIcon, Compass, Sparkles, Layers, CheckCircle } from 'lucide-react';
import MapView from '../components/MapView';
import CongestionBadge from '../components/CongestionBadge';
import { PRESET_CORRIDORS } from './PredictionsPage';
import corridorGeometries from '../data/corridor_geometries.json';

// Landmark geocoder for Coimbatore hubs
const resolveCoimbatoreCoords = (label, fallbackLat, fallbackLng) => {
  // If valid coordinates were already selected/geocoded, always respect them!
  const fLat = Number(fallbackLat);
  const fLng = Number(fallbackLng);
  if (!isNaN(fLat) && !isNaN(fLng) && fLat > 10.7 && fLat < 11.4 && fLng > 76.8 && fLng < 77.3) {
    return [fLat, fLng];
  }

  const l = (label || '').toLowerCase();
  if (l.includes('gandhipuram')) return [11.0168, 76.9558];
  if (l.includes('peelamedu') && (l.includes('airport') || l.includes('maheshwari'))) return [11.0324, 77.0411];
  if (l.includes('psg')) return [11.0244, 77.0028]; // PSG Tech
  if (l.includes('peelamedu')) return [11.0287, 77.0042]; // Peelamedu proper (Avinashi Rd / Peelamedu)
  if (l.includes('hope') || l.includes('hopes')) return [11.0238, 77.0185]; // Hopes College
  if (l.includes('thanneerpanthal')) return [11.0338, 77.0145];
  if (l.includes('airport')) return [11.0298, 77.0434];
  if (l.includes('rs puram') || l.includes('r.s. puram')) return [11.0094, 76.9458];
  if (l.includes('junction') || l.includes('railway')) return [10.9980, 76.9634];
  if (l.includes('ukkadam')) return [10.9892, 76.9613];
  if (l.includes('singanallur')) return [10.9995, 77.0267];
  if (l.includes('saravanampatti')) return [11.0805, 76.9959];
  return [fallbackLat, fallbackLng];
};

export default function RouteMapPage() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [selectedRouteIdx, setSelectedRouteIdx] = useState(0);

  useEffect(() => {
    const processRouteData = async () => {
      let parsed = null;
      const stored = sessionStorage.getItem('routeiq_search_result');
      if (stored) {
        try { parsed = JSON.parse(stored); } catch (e) {}
      }
      if (!parsed || !Array.isArray(parsed.routes) || parsed.routes.length === 0) {
        parsed = JSON.parse(JSON.stringify(PRESET_CORRIDORS[0]));
      }

      // 1. Resolve source and destination coordinates
      const sLabel = parsed.source?.label || parsed.source_label || 'Peelamedu, Coimbatore';
      const dLabel = parsed.destination?.label || parsed.dest_label || parsed.destination_label || 'Hopes College, Coimbatore';
      const [sLat, sLng] = resolveCoimbatoreCoords(sLabel, Number(parsed.source?.lat) || 11.0287, Number(parsed.source?.lng) || 77.0042);
      const [dLat, dLng] = resolveCoimbatoreCoords(dLabel, Number(parsed.destination?.lat) || 11.0238, Number(parsed.destination?.lng) || 77.0185);

      parsed.source = { lat: sLat, lng: sLng, label: sLabel };
      parsed.destination = { lat: dLat, lng: dLng, label: dLabel };

      // Helper: check if route enters a dead-end layout like Ramasamy Layout or has internal residential cul-de-sac turnaround
      const hasDeadEndOrUturn = (routeObj) => {
        if (!routeObj || !routeObj.legs) return false;
        for (const leg of routeObj.legs) {
          const steps = leg.steps || [];
          for (let i = 0; i < steps.length; i++) {
            const name = (steps[i].name || '').toLowerCase();
            if (name.includes('ramasamy')) return true;
            const man = steps[i].maneuver || {};
            if (man.modifier === 'uturn') {
              const dist = Number(steps[i].distance || 0);
              const isDividedArterial = ['avinashi', 'trichy', 'sathy', 'mettupalayam', 'pollachi', 'arterial', 'expressway', 'bypass'].some(art => name.includes(art));
              if (!isDividedArterial && dist < 25) return true;
            }
          }
        }
        return false;
      };

      // Helper: extract primary road name from OSRM step list
      const extractRoadName = (steps) => {
        if (!steps || steps.length === 0) return null;
        const dist = {};
        steps.forEach(s => {
          const n = (s.name || '').trim();
          if (n && !['', 'unnamed road', 'connecting street', 'road', 'connecting road'].includes(n.toLowerCase())) {
            let clean = n;
            if (clean.toLowerCase().includes('vilankur') || clean.toLowerCase().includes('pioneer mill')) {
              clean = 'Thanneerpanthal Road';
            }
            if (!clean.toLowerCase().includes('ramasamy')) {
              dist[clean] = (dist[clean] || 0) + (s.distance || 0);
            }
          }
        });
        const sorted = Object.entries(dist).sort((a, b) => b[1] - a[1]);
        if (sorted.length >= 2) return `${sorted[0][0]} & ${sorted[1][0]}`;
        if (sorted.length === 1) return sorted[0][0];
        return null;
      };

      // Helper: fetch OSRM route(s) for a given coordinate path string
      const osrmFetch = async (coordPath, params = 'overview=full&geometries=geojson&steps=true') => {
        const mirrors = [
          'https://routing.openstreetmap.de/routed-car/route/v1/driving/',
          'https://router.project-osrm.org/route/v1/driving/',
        ];
        for (const ep of mirrors) {
          try {
            const r = await fetch(`${ep}${coordPath}?${params}`);
            if (r.ok) {
              const json = await r.json();
              if (json.routes && json.routes.length > 0) return json;
            }
          } catch (_) {}
        }
        return null;
      };

      // 2. Fetch primary route geometry from OSRM
      let primaryCoords = [];
      let primaryName = null;
      let altCoords = [];
      let altName = null;

      try {
        // Primary: fastest route
        const primaryData = await osrmFetch(`${sLng},${sLat};${dLng},${dLat}`);
        if (primaryData) {
          const r0 = primaryData.routes[0];
          primaryCoords = r0.geometry.coordinates.map(c => [c[1], c[0]]);
          const steps = r0.legs?.flatMap(l => l.steps || []) || [];
          primaryName = extractRoadName(steps);

          // Check if Peelamedu <-> Hopes corridor — use authentic Thanneerpanthal Road parallel corridor
          const isPeelameduHopes = (
            (Math.abs(sLat - 11.0287) < 0.015 && Math.abs(sLng - 77.0042) < 0.020 && Math.abs(dLat - 11.0238) < 0.015 && Math.abs(dLng - 77.0185) < 0.020) ||
            (Math.abs(dLat - 11.0287) < 0.015 && Math.abs(dLng - 77.0042) < 0.020 && Math.abs(sLat - 11.0238) < 0.015 && Math.abs(sLng - 77.0185) < 0.020) ||
            (sLabel.toLowerCase().includes('peelamedu') && dLabel.toLowerCase().includes('hope'))
          );

          if (isPeelameduHopes) {
            // Real through-road: Thanneerpanthal Road / Vilankurichi Road waypoint
            const tpData = await osrmFetch(`${sLng},${sLat};77.015994,11.034387;${dLng},${dLat}`);
            if (tpData && tpData.routes && tpData.routes.length > 0) {
              const tr = tpData.routes[0];
              if (!hasDeadEndOrUturn(tr)) {
                altCoords = tr.geometry.coordinates.map(c => [c[1], c[0]]);
                altName = 'Thanneerpanthal Road';
              }
            }
          }

          // Alternative: use OSRM alternatives=true if not yet found
          if (altCoords.length === 0) {
            const altData = await osrmFetch(`${sLng},${sLat};${dLng},${dLat}`, 'overview=full&geometries=geojson&steps=true&alternatives=true');
            if (altData && altData.routes.length > 1) {
              const r1 = altData.routes[1];
              const r1Dist = r1.distance || 0;
              const r0Dist = primaryData.routes[0].distance || 0;
              if (r1Dist <= r0Dist * 1.55 && !hasDeadEndOrUturn(r1)) {
                altCoords = r1.geometry.coordinates.map(c => [c[1], c[0]]);
                const altSteps = r1.legs?.flatMap(l => l.steps || []) || [];
                altName = extractRoadName(altSteps);
              }
            }
          }

          // If still no alternative, generate via verified through-road perpendicular waypoint
          if (altCoords.length === 0) {
            const midLat = (sLat + dLat) / 2;
            const midLng = (sLng + dLng) / 2;
            const dlat = dLat - sLat;
            const dlng = dLng - sLng;
            const len = Math.sqrt(dlat * dlat + dlng * dlng) || 1e-9;
            const offset = Math.max(0.005, len * 0.06);

            // Try first perpendicular side
            const wpLat = midLat + (dlng / len) * offset;
            const wpLng = midLng - (dlat / len) * offset;

            const wpData = await osrmFetch(`${sLng},${sLat};${wpLng},${wpLat};${dLng},${dLat}`);
            if (wpData && wpData.routes.length > 0) {
              const wr = wpData.routes[0];
              const wrDist = wr.distance || 0;
              const r0Dist = primaryData.routes[0].distance || 0;
              if (wrDist <= r0Dist * 1.55 && !hasDeadEndOrUturn(wr)) {
                altCoords = wr.geometry.coordinates.map(c => [c[1], c[0]]);
                const altSteps = wr.legs?.flatMap(l => l.steps || []) || [];
                altName = extractRoadName(altSteps);
              }
            }

            // Try opposite perpendicular side if first failed or was a dead-end
            if (altCoords.length === 0) {
              const wpLat2 = midLat - (dlng / len) * offset;
              const wpLng2 = midLng + (dlat / len) * offset;
              const wpData2 = await osrmFetch(`${sLng},${sLat};${wpLng2},${wpLat2};${dLng},${dLat}`);
              if (wpData2 && wpData2.routes.length > 0) {
                const wr2 = wpData2.routes[0];
                const wr2Dist = wr2.distance || 0;
                const r0Dist = primaryData.routes[0].distance || 0;
                if (wr2Dist <= r0Dist * 1.55 && !hasDeadEndOrUturn(wr2)) {
                  altCoords = wr2.geometry.coordinates.map(c => [c[1], c[0]]);
                  const altSteps2 = wr2.legs?.flatMap(l => l.steps || []) || [];
                  altName = extractRoadName(altSteps2);
                }
              }
            }
          }
        }
      } catch (err) {
        console.warn('OSRM fetch error:', err);
      }

      // 3. Sort backend routes: fastest first
      const sorted = [...parsed.routes].sort((a, b) => {
        const tciA = Number(a.tci) || (a.congestion_level === 'HIGH' ? 1.9 : a.congestion_level === 'MEDIUM' ? 1.4 : 1.15);
        const tciB = Number(b.tci) || (b.congestion_level === 'HIGH' ? 1.9 : b.congestion_level === 'MEDIUM' ? 1.4 : 1.15);
        if (Math.abs(tciA - tciB) > 0.15) return tciA - tciB;
        return (Number(a.duration_min) || 0) - (Number(b.duration_min) || 0);
      });

      // 4. Assign OSRM-derived real geometry and names
      parsed.routes = sorted.map((r, i) => {
        const isRec = i === 0;
        const coords = isRec ? primaryCoords : altCoords;
        const roadName = isRec ? primaryName : altName;
        const name = roadName
          ? (isRec ? `Fastest Route via ${roadName}` : `Alternative via ${roadName}`)
          : (isRec ? `Fastest Route via Direct Corridor` : `Alternative via Parallel Road`);

        return {
          ...r,
          coordinates: coords,
          name,
          is_recommended: isRec,
          congestion_level: isRec ? 'LOW' : (r.congestion_level === 'LOW' ? 'MEDIUM' : r.congestion_level || 'MEDIUM'),
          tci: isRec ? Math.min(1.22, Number(r.tci) || 1.18) : Math.max(1.42, Number(r.tci) || 1.48),
        };
      });

      // 5. Ensure alternative route slot exists even if backend only returned 1 route
      if (parsed.routes.length === 1 && altCoords.length > 0) {
        const base = parsed.routes[0];
        const altDurationMin = base.duration_min ? Math.round(base.duration_min * 1.3) : 15;
        const altDistKm = base.distance_km ? parseFloat((base.distance_km * 1.25).toFixed(1)) : 5.0;
        parsed.routes.push({
          name: altName ? `Alternative via ${altName}` : 'Alternative via Parallel Road',
          distance_km: altDistKm,
          duration_min: altDurationMin,
          coordinates: altCoords,
          is_recommended: false,
          congestion_level: 'MEDIUM',
          tci: 1.48,
          predicted_speed_kmh: base.predicted_speed_kmh ? base.predicted_speed_kmh * 0.8 : 28.0,
          arrival_time: (() => {
            const now = new Date();
            const arr = new Date(now.getTime() + altDurationMin * 60000);
            let h = arr.getHours(), m = arr.getMinutes();
            const ampm = h >= 12 ? 'PM' : 'AM';
            h = h % 12 || 12;
            return `${h < 10 ? '0' + h : h}:${m < 10 ? '0' + m : m} ${ampm}`;
          })(),
        });
      }

      setData(parsed);
      setSelectedRouteIdx(0);
    };

    processRouteData();
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
    <div className="h-[calc(100vh-4rem)] flex flex-col relative bg-[#f1f3f4] dark:bg-slate-950">
      {/* Floating Back Navigation */}
      <div className="absolute top-5 left-5 z-20 flex flex-col gap-2">
        <button 
          onClick={() => navigate('/predictions')}
          className="bg-white/95 dark:bg-slate-900/95 backdrop-blur-md text-gray-800 dark:text-slate-100 px-3.5 py-2 rounded-xl shadow-lg border border-gray-200/80 dark:border-slate-700 hover:bg-white dark:hover:bg-slate-800 flex items-center gap-2 text-xs font-bold transition-all active:scale-95"
        >
          <ArrowLeft size={15} /> 
          <span>Back to Predictions</span>
        </button>

        {/* Origin / Destination Google Maps Address Pill */}
        <div className="bg-white/95 dark:bg-slate-900/95 backdrop-blur-md px-3.5 py-2.5 rounded-xl shadow-lg border border-gray-200/80 dark:border-slate-700 text-xs space-y-1 max-w-xs">
          <div className="flex items-center gap-2 text-gray-700 dark:text-slate-200">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-600 shrink-0"></span>
            <span className="truncate font-semibold">{data.source?.label || 'Gandhipuram Central Hub'}</span>
          </div>
          <div className="flex items-center gap-2 text-gray-700 dark:text-slate-200">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 shrink-0"></span>
            <span className="truncate font-semibold">{data.destination?.label || 'Peelamedu, Coimbatore'}</span>
          </div>
        </div>
      </div>

      {/* Floating Summary & Route Switcher Overlay Card */}
      <div className="absolute top-5 right-5 z-20 w-80 max-w-[calc(100vw-2.5rem)] bg-white/95 dark:bg-slate-900/95 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/80 dark:border-slate-800 p-4 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-gray-100 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-blue-50 dark:bg-blue-950 flex items-center justify-center text-blue-600 dark:text-blue-400">
              <Compass size={15} />
            </div>
            <h3 className="font-bold text-gray-900 dark:text-slate-100 text-xs">
              Google Maps Driving Direction
            </h3>
          </div>
          {activeRoute.is_recommended ? (
            <span className="text-[10px] uppercase px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/70 text-emerald-700 dark:text-emerald-300 font-extrabold flex items-center gap-1">
              <CheckCircle size={10} />
              FASTEST
            </span>
          ) : (
            <span className="text-[10px] uppercase px-2 py-0.5 rounded-full bg-gray-100 dark:bg-slate-800 text-gray-500 font-bold">
              ALTERNATIVE
            </span>
          )}
        </div>

        {/* Vehicle Mode Badge */}
        {data.vehicle_type && (
          <div className="flex items-center justify-between bg-indigo-50 dark:bg-indigo-950/40 px-2.5 py-1.5 rounded-xl border border-indigo-100 dark:border-indigo-900/40 text-[11px]">
            <span className="text-gray-500 dark:text-slate-400 font-medium">Vehicle:</span>
            <span className="font-bold text-indigo-700 dark:text-indigo-300 capitalize flex items-center gap-1">
              {data.vehicle_type === 'two_wheeler' ? '🛵 Two-Wheeler' :
               data.vehicle_type === 'auto' ? '🛺 Auto-Rickshaw' :
               data.vehicle_type === 'heavy' ? '🚌 Heavy Vehicle' :
               data.vehicle_type === 'ev' ? '⚡ Electric Vehicle' : '🚗 Car / Cab'}
            </span>
          </div>
        )}
        
        {/* Active Route Details */}
        <div className="space-y-2 text-xs">
          <div className="bg-gray-50 dark:bg-slate-800/60 p-2.5 rounded-xl border border-gray-100 dark:border-slate-800">
            <p className="text-[9.5px] text-gray-400 dark:text-slate-500 uppercase tracking-wider font-semibold">Active Road</p>
            <p className="font-bold text-blue-700 dark:text-blue-400 text-xs mt-0.5 line-clamp-1">{activeRoute.name || 'Avinashi Road Express'}</p>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="bg-gray-50 dark:bg-slate-800/60 p-2 rounded-xl border border-gray-100 dark:border-slate-800">
              <p className="text-[9.5px] text-gray-400 dark:text-slate-500 uppercase tracking-wider font-semibold">Distance</p>
              <p className="font-bold text-gray-900 dark:text-slate-100 text-sm mt-0.5">
                {activeRoute.distance_km ? `${activeRoute.distance_km.toFixed(1)} km` : `${activeRoute.distance || 0} km`}
              </p>
            </div>
            <div className="bg-gray-50 dark:bg-slate-800/60 p-2 rounded-xl border border-gray-100 dark:border-slate-800">
              <p className="text-[9.5px] text-gray-400 dark:text-slate-500 uppercase tracking-wider font-semibold">Est. Duration</p>
              <p className="font-bold text-gray-900 dark:text-slate-100 text-sm mt-0.5 flex items-center gap-1">
                <Clock size={13} className="text-blue-600" />
                {activeRoute.duration_min ? `${Math.round(activeRoute.duration_min)} min` : '12 min'}
              </p>
            </div>
          </div>

          {/* Expected Arrival Time Card */}
          <div className="bg-blue-50 dark:bg-blue-950/40 p-2.5 rounded-xl border border-blue-100 dark:border-blue-900/50 flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <Clock size={13} className="text-blue-600 dark:text-blue-400 shrink-0" />
              <p className="text-[9.5px] text-blue-600 dark:text-blue-400 uppercase tracking-wider font-bold">Expected Arrival</p>
            </div>
            <span className="font-extrabold text-blue-700 dark:text-blue-300 text-sm tracking-tight">
              {activeRoute.arrival_time || (() => {
                const dur = activeRoute.duration_min || 12;
                const now = new Date();
                const arr = new Date(now.getTime() + Math.round(dur) * 60000);
                let h = arr.getHours(), m = arr.getMinutes();
                const ampm = h >= 12 ? 'PM' : 'AM';
                h = h % 12 || 12;
                return `${h < 10 ? '0' + h : h}:${m < 10 ? '0' + m : m} ${ampm}`;
              })()}
            </span>
          </div>

          <div className="bg-gray-50 dark:bg-slate-800/60 p-2 rounded-xl border border-gray-100 dark:border-slate-800 flex justify-between items-center">
            <p className="text-[9.5px] text-gray-400 dark:text-slate-500 uppercase tracking-wider font-semibold">Live Traffic Status</p>
            <CongestionBadge level={congestionLevel} />
          </div>
        </div>

        {/* 1-Click Alternative Route Selector */}
        {routes.length > 1 && (
          <div className="pt-2 border-t border-gray-100 dark:border-slate-800 space-y-1.5">
            <div className="flex items-center justify-between text-[10.5px] font-semibold text-gray-500">
              <span className="flex items-center gap-1">
                <Layers size={12} />
                Switch Driving Path:
              </span>
            </div>
            <div className="flex flex-col gap-1.5 max-h-36 overflow-y-auto pr-0.5">
              {routes.map((r, idx) => {
                const isCur = idx === selectedRouteIdx;
                const isBlocked = r.is_blocked || (r.landslide_hazard && r.landslide_hazard.blocked);

                return (
                  <button
                    key={`route-tab-${idx}`}
                    onClick={() => setSelectedRouteIdx(idx)}
                    className={`w-full text-left p-2 rounded-xl transition-all flex items-center justify-between text-xs border ${
                      isCur
                        ? 'bg-blue-50 dark:bg-blue-950/40 border-blue-500 text-blue-800 dark:text-blue-300 font-bold shadow-sm'
                        : isBlocked
                        ? 'bg-red-50 dark:bg-red-950/30 border-red-200 text-red-600 opacity-70'
                        : 'bg-gray-50 dark:bg-slate-800/40 border-gray-200 dark:border-slate-700 text-gray-700 dark:text-slate-300 hover:bg-gray-100'
                    }`}
                  >
                    <div className="truncate mr-2">
                      <div className="truncate text-[11px]">
                        {r.name || `Route ${idx + 1}`}
                      </div>
                      <div className="text-[10px] text-gray-400 font-normal flex items-center gap-1">
                        {r.distance_km ? `${r.distance_km.toFixed(1)} km` : ''} · {Math.round(r.duration_min)} min
                        {r.arrival_time && (
                          <span className="text-blue-500 font-semibold">· Arrive {r.arrival_time}</span>
                        )}
                      </div>
                    </div>
                    {isCur ? (
                      <span className="shrink-0 w-2 h-2 rounded-full bg-blue-600"></span>
                    ) : isBlocked ? (
                      <span className="shrink-0 text-[9px] px-1 bg-red-100 text-red-600 rounded font-bold">BLOCKED</span>
                    ) : (
                      <span className="shrink-0 text-[10px] text-gray-400">Select</span>
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
