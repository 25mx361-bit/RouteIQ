/**
 * frontend/src/components/MapView.jsx
 * High-fidelity Google Maps-style route visualization component.
 * Features:
 *   - Dedicated floating + and − zoom controls & recenter button (bottom-right)
 *   - Clean OpenStreetMap free tiles (NO API Key required, NO watermark)
 *   - Google Maps dual-layer vibrant route polyline (outer shadow casing + inner cyan/blue line)
 *   - Interactive click on any alternative route on the map or its ETA bubble to switch active path
 *   - Turn waypoint dots along route maneuvers
 *   - Mid-route floating ETA duration badges
 *   - Google Maps custom Origin (white halo ring) and Destination (classic Red Pin)
 *   - Proximity-filtered hazard beacons (avoids map clutter)
 *   - Bottom-left positioned legend (no overlap with top-right overlay cards)
 */
import React, { useEffect, useMemo, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle, CircleMarker, useMap } from 'react-leaflet';
import L from 'leaflet';

// ── Google Maps Style Origin Pin (White halo + inner dark center + bold pill label) ──
const createSourceMarkerIcon = (label = 'Origin') => {
  return L.divIcon({
    className: 'google-source-marker',
    html: `
      <div style="position: relative; display: flex; flex-direction: column; align-items: center; cursor: pointer;">
        <div style="
          background: rgba(15, 23, 42, 0.95);
          color: #f8fafc;
          padding: 3px 8px;
          border-radius: 9999px;
          font-size: 11px;
          font-weight: 700;
          letter-spacing: -0.01em;
          border: 1.5px solid #38bdf8;
          box-shadow: 0 4px 12px rgba(0,0,0,0.5);
          white-space: nowrap;
          margin-bottom: 4px;
          display: flex;
          align-items: center;
          gap: 4px;
        ">
          <span style="width: 6px; height: 6px; border-radius: 50%; background: #38bdf8;"></span>
          ${label}
        </div>
        <div style="
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: #ffffff;
          border: 4px solid #0f172a;
          box-shadow: 0 2px 8px rgba(0,0,0,0.6), 0 0 0 2px #38bdf8;
        "></div>
      </div>
    `,
    iconSize: [120, 48],
    iconAnchor: [60, 44],
    popupAnchor: [0, -44],
  });
};

// ── Google Maps Style Destination Pin (Red Teardrop Pin + bold pill label) ──
const createDestMarkerIcon = (label = 'Destination') => {
  return L.divIcon({
    className: 'google-dest-marker',
    html: `
      <div style="position: relative; display: flex; flex-direction: column; align-items: center; cursor: pointer;">
        <div style="
          background: rgba(15, 23, 42, 0.95);
          color: #f8fafc;
          padding: 3px 8px;
          border-radius: 9999px;
          font-size: 11px;
          font-weight: 700;
          letter-spacing: -0.01em;
          border: 1.5px solid #ef4444;
          box-shadow: 0 4px 12px rgba(0,0,0,0.5);
          white-space: nowrap;
          margin-bottom: 4px;
          display: flex;
          align-items: center;
          gap: 4px;
        ">
          <span style="width: 6px; height: 6px; border-radius: 50%; background: #ef4444;"></span>
          ${label}
        </div>
        <svg width="26" height="34" viewBox="0 0 26 34" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 4px 6px rgba(0,0,0,0.5));">
          <path d="M13 0C5.82 0 0 5.82 0 13C0 22.75 13 34 13 34C13 34 26 22.75 26 13C26 5.82 20.18 0 13 0Z" fill="#EF4444"/>
          <circle cx="13" cy="12" r="5.5" fill="#FFFFFF"/>
          <circle cx="13" cy="12" r="3" fill="#B91C1C"/>
        </svg>
      </div>
    `,
    iconSize: [140, 60],
    iconAnchor: [70, 58],
    popupAnchor: [0, -58],
  });
};

// ── Google Maps Style Mid-Route Floating Duration ETA Badge ──
const createEtaBadgeIcon = (durationMin = 15, isSelected = true) => {
  const bg = isSelected ? '#0f172a' : '#334155';
  const border = isSelected ? '#38bdf8' : '#64748b';
  const opacity = isSelected ? '1' : '0.85';
  return L.divIcon({
    className: 'google-eta-badge',
    html: `
      <div style="
        background: ${bg};
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: -0.02em;
        border: 1.5px solid ${border};
        box-shadow: 0 4px 14px rgba(0,0,0,0.6);
        display: flex;
        align-items: center;
        gap: 6px;
        white-space: nowrap;
        opacity: ${opacity};
        cursor: pointer;
        transform: translate(-50%, -50%);
      ">
        <span style="font-size: 13px;">🚗</span>
        <span>${Math.round(durationMin)} min</span>
      </div>
    `,
    iconSize: [80, 30],
    iconAnchor: [40, 15],
  });
};

// ── Red Hazard Beacon for Proximate Landslides ──
const createLandslideIcon = (severity) => {
  return L.divIcon({
    className: 'custom-landslide-marker',
    html: `
      <div style="position: relative; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">
        <span style="
          position: absolute;
          width: 32px;
          height: 32px;
          background: rgba(239, 68, 68, 0.45);
          border-radius: 50%;
          animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
        "></span>
        <div style="
          position: relative;
          width: 24px;
          height: 24px;
          background: #dc2626;
          border: 2px solid #ffffff;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 8px rgba(0,0,0,0.5);
          color: #ffffff;
          font-weight: bold;
          font-size: 12px;
        ">⚠️</div>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16],
  });
};

// ── Auto Bounds Handler ──
function MapBoundsHandler({ sourceCoords, destCoords, routes }) {
  const map = useMap();

  const fitAllPoints = useCallback(() => {
    const points = [];

    if (sourceCoords && sourceCoords.lat && sourceCoords.lng) {
      points.push([sourceCoords.lat, sourceCoords.lng]);
    }
    if (destCoords && destCoords.lat && destCoords.lng) {
      points.push([destCoords.lat, destCoords.lng]);
    }

    if (routes && routes.length > 0) {
      routes.forEach((r) => {
        const coords = r.coordinates || [];
        coords.forEach((pt) => {
          if (Array.isArray(pt) && pt.length >= 2) {
            points.push([pt[0], pt[1]]);
          }
        });
      });
    }

    if (points.length === 1) {
      map.setView(points[0], 14, { animate: true });
    } else if (points.length > 1) {
      const bounds = L.latLngBounds(points);
      map.fitBounds(bounds, { padding: [70, 70], maxZoom: 16, animate: true });
    }
  }, [sourceCoords, destCoords, routes, map]);

  useEffect(() => {
    fitAllPoints();
  }, [fitAllPoints]);

  return (
    <div className="absolute bottom-6 right-6 z-[1000] flex flex-col gap-1.5 shadow-2xl">
      {/* Fit / Recenter Button */}
      <button
        onClick={fitAllPoints}
        title="Recenter and Fit Full Route"
        className="w-10 h-10 bg-slate-900/95 hover:bg-slate-800 text-slate-200 hover:text-white rounded-xl flex items-center justify-center border border-slate-700/80 backdrop-blur-md transition-all active:scale-95 shadow-lg text-base font-bold"
      >
        ⌖
      </button>

      <div className="flex flex-col rounded-xl overflow-hidden border border-slate-700/80 shadow-lg">
        {/* Zoom In Button (+) */}
        <button
          onClick={() => map.zoomIn()}
          title="Zoom In (+)"
          className="w-10 h-10 bg-slate-900/95 hover:bg-slate-800 text-slate-200 hover:text-white flex items-center justify-center backdrop-blur-md transition-all active:scale-95 text-xl font-bold border-b border-slate-700/80"
        >
          +
        </button>

        {/* Zoom Out Button (−) */}
        <button
          onClick={() => map.zoomOut()}
          title="Zoom Out (−)"
          className="w-10 h-10 bg-slate-900/95 hover:bg-slate-800 text-slate-200 hover:text-white flex items-center justify-center backdrop-blur-md transition-all active:scale-95 text-xl font-bold"
        >
          −
        </button>
      </div>
    </div>
  );
}

export default function MapView({
  sourceCoords,
  destCoords,
  routes = [],
  landslides = [],
  selectedRoute = 0,
  onSelectRoute,
}) {
  const defaultCenter = [11.0176, 76.9667]; // Gandhipuram Central Coimbatore default
  const defaultZoom = 13;

  const activeRoute = routes[selectedRoute] || routes[0] || null;
  const activeCoords = activeRoute?.coordinates || [];

  // Filter landslides to only show those proximate to the route corridor
  const relevantLandslides = useMemo(() => {
    if (!landslides || landslides.length === 0 || activeCoords.length === 0) return [];
    return landslides.filter((ls) => {
      const lsLat = ls.lat || ls.location?.coordinates?.[1];
      const lsLng = ls.lng || ls.location?.coordinates?.[0];
      if (!lsLat || !lsLng) return false;

      return activeCoords.some((pt) => {
        const dLat = Math.abs(pt[0] - lsLat);
        const dLng = Math.abs(pt[1] - lsLng);
        return dLat < 0.04 && dLng < 0.04;
      });
    });
  }, [landslides, activeCoords]);

  // Find midpoint of active route for floating ETA bubble
  const midPoint = useMemo(() => {
    if (!activeCoords || activeCoords.length === 0) return null;
    const midIdx = Math.floor(activeCoords.length / 2);
    return activeCoords[midIdx];
  }, [activeCoords]);

  // Maneuver waypoint dots along the active route
  const waypointDots = useMemo(() => {
    if (!activeCoords || activeCoords.length < 8) return [];
    const step = Math.max(3, Math.floor(activeCoords.length / 10));
    const dots = [];
    for (let i = step; i < activeCoords.length - step; i += step) {
      dots.push(activeCoords[i]);
    }
    return dots;
  }, [activeCoords]);

  const sourceLabel = sourceCoords?.label || 'Origin';
  const destLabel = destCoords?.label || 'Destination';

  return (
    <div className="relative w-full h-full min-h-[400px] rounded-xl overflow-hidden shadow-2xl border border-slate-800 bg-slate-950">
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        scrollWheelZoom={true}
        zoomControl={false}
        className="w-full h-full"
      >
        {/* Clean OpenStreetMap Tiles — 100% Free, NO API Key, NO watermark */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />

        <MapBoundsHandler
          sourceCoords={sourceCoords}
          destCoords={destCoords}
          routes={routes}
        />

        {/* ── Origin Marker (Google Maps Style) ── */}
        {sourceCoords && sourceCoords.lat && sourceCoords.lng && (
          <Marker
            position={[sourceCoords.lat, sourceCoords.lng]}
            icon={createSourceMarkerIcon(sourceLabel)}
          >
            <Popup>
              <div className="p-1 space-y-1">
                <div className="text-[10px] font-bold uppercase tracking-wider text-sky-400">
                  📍 Origin Location
                </div>
                <div className="text-sm font-semibold text-slate-100">{sourceLabel}</div>
              </div>
            </Popup>
          </Marker>
        )}

        {/* ── Destination Marker (Google Maps Red Pin) ── */}
        {destCoords && destCoords.lat && destCoords.lng && (
          <Marker
            position={[destCoords.lat, destCoords.lng]}
            icon={createDestMarkerIcon(destLabel)}
          >
            <Popup>
              <div className="p-1 space-y-1">
                <div className="text-[10px] font-bold uppercase tracking-wider text-rose-400">
                  🎯 Destination Target
                </div>
                <div className="text-sm font-semibold text-slate-100">{destLabel}</div>
              </div>
            </Popup>
          </Marker>
        )}

        {/* ── Active Landslide Hazard Beacons (Filtered to Route Proximity Only) ── */}
        {relevantLandslides.map((ls, idx) => {
          const lsLat = ls.lat || ls.location?.coordinates?.[1];
          const lsLng = ls.lng || ls.location?.coordinates?.[0];
          if (!lsLat || !lsLng) return null;

          return (
            <React.Fragment key={`landslide-${idx}`}>
              <Marker position={[lsLat, lsLng]} icon={createLandslideIcon(ls.severity)}>
                <Popup>
                  <div className="p-1 space-y-1.5 min-w-[180px]">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] uppercase font-bold text-red-400">
                        🚨 Hazard on Corridor
                      </span>
                      <span className="text-[9px] px-1.5 py-0.5 bg-red-500/20 text-red-300 rounded font-bold">
                        {ls.severity || 'CRITICAL'}
                      </span>
                    </div>
                    <div className="text-xs font-bold text-slate-100">{ls.title}</div>
                    <div className="text-[10px] text-slate-400">{ls.road_name}</div>
                  </div>
                </Popup>
              </Marker>
              <Circle
                center={[lsLat, lsLng]}
                radius={ls.radius_m || 1500}
                pathOptions={{
                  color: '#ef4444',
                  fillColor: '#ef4444',
                  fillOpacity: 0.15,
                  weight: 1.5,
                  dashArray: '4, 4',
                }}
              />
            </React.Fragment>
          );
        })}

        {/* ── Render Alternative Routes (Background Layer with 1-Click Selection) ── */}
        {routes.map((route, idx) => {
          if (idx === selectedRoute) return null; // Rendered separately on top
          const isBlocked = route.is_blocked || (route.landslide_hazard && route.landslide_hazard.blocked);
          const coords = route.coordinates || [];
          if (coords.length === 0) return null;

          const altMidIdx = Math.floor(coords.length / 2);
          const altMidPoint = coords[altMidIdx];

          return (
            <React.Fragment key={`route-alt-group-${idx}`}>
              {/* Invisible wide polyline hit-box for 1-click selection */}
              <Polyline
                positions={coords}
                eventHandlers={{
                  click: () => {
                    if (onSelectRoute) onSelectRoute(idx);
                  },
                }}
                pathOptions={{
                  color: '#000000',
                  weight: 22,
                  opacity: 0.0,
                }}
              />

              {/* Visible Alternative Polyline */}
              <Polyline
                positions={coords}
                eventHandlers={{
                  click: () => {
                    if (onSelectRoute) onSelectRoute(idx);
                  },
                }}
                pathOptions={{
                  color: isBlocked ? '#ef4444' : '#64748b',
                  weight: 5,
                  opacity: 0.75,
                  dashArray: isBlocked ? '6, 8' : null,
                  lineCap: 'round',
                  lineJoin: 'round',
                }}
              >
                <Popup>
                  <div className="p-1 space-y-1 cursor-pointer" onClick={() => onSelectRoute && onSelectRoute(idx)}>
                    <div className="text-xs font-bold text-slate-100">
                      {route.name || `Route Option ${idx + 1}`}
                    </div>
                    <div className="text-xs text-slate-400">
                      {route.distance_km} km · {Math.round(route.duration_min)} mins
                    </div>
                    <div className="text-[10px] text-sky-400 font-semibold mt-1">
                      👆 Click to view this route
                    </div>
                  </div>
                </Popup>
              </Polyline>

              {/* Clickable ETA Badge on Alternative Route */}
              {altMidPoint && !isBlocked && (
                <Marker
                  position={[altMidPoint[0], altMidPoint[1]]}
                  icon={createEtaBadgeIcon(route.duration_min || 20, false)}
                  eventHandlers={{
                    click: () => {
                      if (onSelectRoute) onSelectRoute(idx);
                    },
                  }}
                />
              )}
            </React.Fragment>
          );
        })}

        {/* ── Render Selected Active Route (Google Maps Cyan/Blue Dual Layer) ── */}
        {activeRoute && activeCoords.length > 0 && (
          <React.Fragment>
            {/* Outer dark casing / shadow border */}
            <Polyline
              positions={activeCoords}
              pathOptions={{
                color: '#0f172a',
                weight: 9,
                opacity: 0.95,
                lineCap: 'round',
                lineJoin: 'round',
              }}
            />
            {/* Inner vibrant Google Maps Cyan/Blue Polyline */}
            <Polyline
              positions={activeCoords}
              pathOptions={{
                color: '#00b4d8', // Electric Cyan / Google Blue
                weight: 6,
                opacity: 1.0,
                lineCap: 'round',
                lineJoin: 'round',
              }}
            />

            {/* Turn maneuver dots along the route (Google Maps style) */}
            {waypointDots.map((pt, dotIdx) => (
              <CircleMarker
                key={`waypoint-dot-${dotIdx}`}
                center={[pt[0], pt[1]]}
                radius={3.5}
                pathOptions={{
                  color: '#0f172a',
                  fillColor: '#ffffff',
                  fillOpacity: 1.0,
                  weight: 2,
                }}
              />
            ))}

            {/* Floating ETA Duration Badge over selected route center */}
            {midPoint && (
              <Marker
                position={[midPoint[0], midPoint[1]]}
                icon={createEtaBadgeIcon(activeRoute.duration_min || 15, true)}
                interactive={false}
              />
            )}
          </React.Fragment>
        )}
      </MapContainer>

      {/* ── Floating Legend — Positioned at BOTTOM-LEFT to eliminate any overlap with top overlays ── */}
      <div className="absolute bottom-6 left-6 z-[1000] bg-slate-900/90 backdrop-blur-md border border-slate-800 p-3 rounded-2xl shadow-xl space-y-2 text-xs">
        <div className="text-[10px] font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
          Live Navigation Path
        </div>
        <div className="flex items-center gap-2">
          <span className="w-5 h-1.5 bg-[#00b4d8] rounded-full border border-slate-950"></span>
          <span className="text-slate-200 font-semibold">Active Selected Route</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-5 h-1 bg-slate-500 rounded-full"></span>
          <span className="text-slate-400">Clickable Alternatives</span>
        </div>
        {relevantLandslides.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="w-5 h-1 bg-red-500 rounded-full border-dashed border-red-300"></span>
            <span className="text-red-400 font-medium">Hazard Exclusion</span>
          </div>
        )}
      </div>
    </div>
  );
}
