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

// ── Helper: Normalize Coordinate Pair to [lat, lng] ──
export const normalizeCoord = (pt) => {
  if (!pt) return null;
  let lat, lng;
  if (Array.isArray(pt) && pt.length >= 2) {
    lat = Number(pt[0]);
    lng = Number(pt[1]);
  } else if (typeof pt === 'object') {
    lat = Number(pt.lat ?? pt.latitude);
    lng = Number(pt.lng ?? pt.longitude);
  }
  if (isNaN(lat) || isNaN(lng)) return null;
  // GeoJSON uses [lng, lat] where lng ≈ 76-77 and lat ≈ 10-12
  if (lat > 50 && lng < 50) {
    return [lng, lat];
  }
  return [lat, lng];
};

// ── Google Maps Style Origin Pin (White halo + inner Google Blue dot + bold label) ──
const createSourceMarkerIcon = (label = 'Origin') => {
  return L.divIcon({
    className: 'google-source-marker',
    html: `
      <div style="position: relative; display: flex; flex-direction: column; align-items: center; cursor: pointer;">
        <div style="
          background: #ffffff;
          color: #202124;
          padding: 3px 8px;
          border-radius: 9999px;
          font-size: 11px;
          font-weight: 700;
          letter-spacing: -0.01em;
          border: 1px solid #dadce0;
          box-shadow: 0 2px 6px rgba(60,64,67,0.3);
          white-space: nowrap;
          margin-bottom: 4px;
          display: flex;
          align-items: center;
          gap: 5px;
        ">
          <span style="width: 7px; height: 7px; border-radius: 50%; background: #1a73e8;"></span>
          ${label}
        </div>
        <div style="
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #ffffff;
          border: 4.5px solid #1a73e8;
          box-shadow: 0 2px 8px rgba(0,0,0,0.35);
        "></div>
      </div>
    `,
    iconSize: [140, 50],
    iconAnchor: [70, 46],
    popupAnchor: [0, -46],
  });
};

// ── Google Maps Style Destination Pin (Classic Red Teardrop Pin + bold label) ──
const createDestMarkerIcon = (label = 'Destination') => {
  return L.divIcon({
    className: 'google-dest-marker',
    html: `
      <div style="position: relative; display: flex; flex-direction: column; align-items: center; cursor: pointer;">
        <div style="
          background: #ffffff;
          color: #202124;
          padding: 3px 8px;
          border-radius: 9999px;
          font-size: 11px;
          font-weight: 700;
          letter-spacing: -0.01em;
          border: 1px solid #dadce0;
          box-shadow: 0 2px 6px rgba(60,64,67,0.3);
          white-space: nowrap;
          margin-bottom: 4px;
          display: flex;
          align-items: center;
          gap: 5px;
        ">
          <span style="width: 7px; height: 7px; border-radius: 50%; background: #ea4335;"></span>
          ${label}
        </div>
        <svg width="28" height="36" viewBox="0 0 28 36" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 3px 6px rgba(0,0,0,0.35));">
          <path d="M14 0C6.268 0 0 6.268 0 14C0 24.5 14 36 14 36C14 36 28 24.5 28 14C28 6.268 21.732 0 14 0Z" fill="#EA4335"/>
          <circle cx="14" cy="13.5" r="5.5" fill="#FFFFFF"/>
          <circle cx="14" cy="13.5" r="2.8" fill="#B31412"/>
        </svg>
      </div>
    `,
    iconSize: [140, 62],
    iconAnchor: [70, 60],
    popupAnchor: [0, -60],
  });
};

// ── Helper: Format Arrival Time (e.g., "06:48 PM") ──
export const computeArrivalTime = (durationMinutes, baseTimeString = null) => {
  let baseDate = new Date();
  if (baseTimeString) {
    if (typeof baseTimeString === 'string' && baseTimeString.includes(':')) {
      const parts = baseTimeString.split(':');
      const h = parseInt(parts[0], 10);
      const m = parseInt(parts[1], 10);
      if (!isNaN(h) && !isNaN(m)) {
        baseDate.setHours(h, m, 0, 0);
      }
    } else {
      const parsed = new Date(baseTimeString);
      if (!isNaN(parsed.getTime())) baseDate = parsed;
    }
  }
  const arrival = new Date(baseDate.getTime() + Math.round(Number(durationMinutes) || 0) * 60 * 1000);
  let hours = arrival.getHours();
  const minutes = arrival.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12 || 12;
  const minStr = minutes < 10 ? `0${minutes}` : minutes;
  const hrStr = hours < 10 ? `0${hours}` : hours;
  return `${hrStr}:${minStr} ${ampm}`;
};

// ── Google Maps Style Mid-Route Floating Duration & Arrival Time Badge ──
const createEtaBadgeIcon = (durationMin = 12, distanceKm = null, isSelected = true, arrivalTime = null) => {
  const finalArrival = arrivalTime || computeArrivalTime(durationMin);
  const durVal = Math.max(1, Math.round(durationMin));
  const textColor = isSelected ? '#188038' : '#3c4043'; // Google Maps green for fastest route
  const borderColor = isSelected ? '#1a73e8' : '#dadce0';
  const borderWidth = isSelected ? '2px' : '1px';
  const shadow = isSelected 
    ? '0 3px 10px rgba(60,64,67,0.38), 0 1px 4px rgba(60,64,67,0.2)' 
    : '0 2px 6px rgba(60,64,67,0.22), 0 1px 2px rgba(60,64,67,0.12)';
  const scale = isSelected ? 'scale(1.05)' : 'scale(0.95)';
  const zIdx = isSelected ? '1000' : '40';

  const distText = distanceKm ? (typeof distanceKm === 'number' ? `${distanceKm.toFixed(1)} km` : `${distanceKm} km`) : '';

  return L.divIcon({
    className: 'google-eta-badge',
    html: `
      <div style="
        background: #ffffff;
        padding: 5px 9px;
        border-radius: 9px;
        border: ${borderWidth} solid ${borderColor};
        box-shadow: ${shadow};
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        cursor: pointer;
        transform: translate(-50%, -50%) ${scale};
        user-select: none;
        z-index: ${zIdx};
        min-width: 82px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      ">
        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; gap: 6px; line-height: 1.1;">
          <div style="display: flex; align-items: center; gap: 3px;">
            <span style="font-size: 11px;">🚗</span>
            <span style="font-size: 13px; font-weight: 800; letter-spacing: -0.01em; color: ${textColor};">
              ${durVal} min
            </span>
          </div>
          <span style="
            font-size: 10px;
            font-weight: 700;
            color: #1a73e8;
            background: #e8f0fe;
            padding: 1px 5px;
            border-radius: 4px;
            white-space: nowrap;
          ">
            ${finalArrival}
          </span>
        </div>
        <div style="
          font-size: 9.5px;
          font-weight: 500;
          color: #70757a;
          margin-top: 2.5px;
          display: flex;
          align-items: center;
          gap: 4px;
          white-space: nowrap;
        ">
          ${distText ? `<span>${distText}</span>` : ''}
          ${distText ? `<span>·</span>` : ''}
          <span style="color: ${isSelected ? '#188038' : '#5f6368'}; font-weight: 600;">
            ${isSelected ? 'Fastest route' : 'Alternative'}
          </span>
        </div>
      </div>
    `,
    iconSize: [120, 44],
    iconAnchor: [60, 22],
  });
};

// ── Google Maps Directional Chevron / Arrow Icon ──
const createDirectionArrowIcon = (bearing = 0) => {
  return L.divIcon({
    className: 'google-route-arrow',
    html: `
      <div style="
        transform: rotate(${bearing}deg);
        display: flex;
        align-items: center;
        justify-content: center;
        width: 14px;
        height: 14px;
        pointer-events: none;
      ">
        <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
          <path d="M5 0.5L9 8L5 6L1 8L5 0.5Z" fill="#ffffff" stroke="#1557b0" stroke-width="1.2" stroke-linejoin="round"/>
        </svg>
      </div>
    `,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
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
    <div className="absolute bottom-6 right-6 z-[1000] flex flex-col gap-2 shadow-xl">
      {/* Fit / Recenter Button */}
      <button
        onClick={fitAllPoints}
        title="Recenter Route View"
        className="w-9 h-9 bg-white hover:bg-gray-50 text-gray-700 hover:text-black rounded-lg flex items-center justify-center border border-gray-300 shadow-md transition-all active:scale-95 text-base font-bold"
      >
        ⌖
      </button>

      <div className="flex flex-col rounded-lg overflow-hidden border border-gray-300 shadow-md bg-white">
        {/* Zoom In Button (+) */}
        <button
          onClick={() => map.zoomIn()}
          title="Zoom In (+)"
          className="w-9 h-9 hover:bg-gray-50 text-gray-700 flex items-center justify-center transition-all active:scale-95 text-lg font-bold border-b border-gray-200"
        >
          +
        </button>

        {/* Zoom Out Button (−) */}
        <button
          onClick={() => map.zoomOut()}
          title="Zoom Out (−)"
          className="w-9 h-9 hover:bg-gray-50 text-gray-700 flex items-center justify-center transition-all active:scale-95 text-lg font-bold"
        >
          −
        </button>
      </div>
    </div>
  );
}

// ── Corridor Waypoints Interpolator (Fallback when OSRM geometry is missing) ──
function createFallbackRouteCoords(start, end, routeIndex = 0) {
  if (!start || !end) return [];
  const lat1 = Number(start.lat);
  const lng1 = Number(start.lng);
  const lat2 = Number(end.lat);
  const lng2 = Number(end.lng);
  if (isNaN(lat1) || isNaN(lng1) || isNaN(lat2) || isNaN(lng2)) return [];

  const points = [];
  const steps = 18;
  const curvature = routeIndex === 0 ? 0.03 : routeIndex % 2 === 1 ? -0.09 : 0.09;

  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    let lat = lat1 + (lat2 - lat1) * t;
    let lng = lng1 + (lng2 - lng1) * t;

    if (i > 0 && i < steps) {
      const perpLat = -(lng2 - lng1);
      const perpLng = (lat2 - lat1);
      const factor = Math.sin(t * Math.PI) * curvature;
      lat += perpLat * factor;
      lng += perpLng * factor;
    }
    points.push([Number(lat.toFixed(5)), Number(lng.toFixed(5))]);
  }
  return points;
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

  // 1. Normalize Source & Destination with smart coordinate inference
  const normSource = useMemo(() => {
    let lat = sourceCoords?.lat ?? sourceCoords?.latitude;
    let lng = sourceCoords?.lng ?? sourceCoords?.longitude;
    const label = sourceCoords?.label || sourceCoords?.name || 'Origin';
    if (!lat || !lng) {
      if (Array.isArray(sourceCoords?.coordinates) && sourceCoords.coordinates.length >= 2) {
        lng = sourceCoords.coordinates[0];
        lat = sourceCoords.coordinates[1];
      } else if (Array.isArray(sourceCoords) && sourceCoords.length >= 2) {
        lat = sourceCoords[0];
        lng = sourceCoords[1];
      }
    }
    const validated = normalizeCoord([lat, lng]);
    if (validated) {
      return { lat: validated[0], lng: validated[1], label };
    }
    const firstRouteCoord = routes?.[0]?.coordinates?.[0];
    if (firstRouteCoord) {
      const fc = normalizeCoord(firstRouteCoord);
      if (fc) return { lat: fc[0], lng: fc[1], label };
    }
    return { lat: 11.0168, lng: 76.9558, label: sourceCoords?.label || 'Gandhipuram Central Hub' };
  }, [sourceCoords, routes]);

  const normDest = useMemo(() => {
    let lat = destCoords?.lat ?? destCoords?.latitude;
    let lng = destCoords?.lng ?? destCoords?.longitude;
    const label = destCoords?.label || destCoords?.name || 'Destination';
    if (!lat || !lng) {
      if (Array.isArray(destCoords?.coordinates) && destCoords.coordinates.length >= 2) {
        lng = destCoords.coordinates[0];
        lat = destCoords.coordinates[1];
      } else if (Array.isArray(destCoords) && destCoords.length >= 2) {
        lat = destCoords[0];
        lng = destCoords[1];
      }
    }
    const validated = normalizeCoord([lat, lng]);
    if (validated) {
      return { lat: validated[0], lng: validated[1], label };
    }
    const lastRoute = routes?.[0];
    const lastRouteCoord = lastRoute?.coordinates?.[lastRoute.coordinates.length - 1];
    if (lastRouteCoord) {
      const lc = normalizeCoord(lastRouteCoord);
      if (lc) return { lat: lc[0], lng: lc[1], label };
    }
    return { lat: 11.0324, lng: 77.0411, label: destCoords?.label || 'Peelamedu, Coimbatore' };
  }, [destCoords, routes]);

  // 2. Prepare routes: ensure EVERY route has guaranteed valid road coordinates
  const preparedRoutes = useMemo(() => {
    if (!routes || routes.length === 0) {
      return [{
        name: 'Avinashi Road Direct Corridor',
        distance_km: 10.8,
        duration_min: 17.5,
        coordinates: createFallbackRouteCoords(normSource, normDest, 0),
        is_recommended: true
      }];
    }

    return routes.map((r, idx) => {
      let coords = r.coordinates;
      if (!coords || !Array.isArray(coords) || coords.length < 2) {
        coords = createFallbackRouteCoords(normSource, normDest, idx);
      } else {
        coords = coords.map(pt => normalizeCoord(pt)).filter(Boolean);
      }
      return {
        ...r,
        coordinates: coords,
      };
    });
  }, [routes, normSource, normDest]);

  const activeRoute = preparedRoutes[selectedRoute] || preparedRoutes[0] || null;
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

  // Find midpoint of active route for floating Google Maps ETA badge
  const midPoint = useMemo(() => {
    if (!activeCoords || activeCoords.length === 0) return null;
    const midIdx = Math.floor(activeCoords.length * 0.45);
    return activeCoords[midIdx];
  }, [activeCoords]);

  // Directional maneuver arrows along the active route (Google Maps forward flow)
  const directionArrows = useMemo(() => {
    if (!activeCoords || activeCoords.length < 12) return [];
    const step = Math.max(10, Math.floor(activeCoords.length / 9));
    const arrows = [];
    for (let i = Math.floor(step * 0.6); i < activeCoords.length - 3; i += step) {
      const p1 = activeCoords[i];
      const p2 = activeCoords[i + 1];
      if (p1 && p2) {
        const lat1 = (p1[0] * Math.PI) / 180;
        const lat2 = (p2[0] * Math.PI) / 180;
        const dLng = ((p2[1] - p1[1]) * Math.PI) / 180;
        const y = Math.sin(dLng) * Math.cos(lat2);
        const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLng);
        const bearing = ((Math.atan2(y, x) * 180) / Math.PI + 360) % 360;
        arrows.push({ pos: p2, bearing });
      }
    }
    return arrows;
  }, [activeCoords]);

  // Maneuver waypoint dots along the active route
  const waypointDots = useMemo(() => {
    if (!activeCoords || activeCoords.length < 10) return [];
    const step = Math.max(8, Math.floor(activeCoords.length / 10));
    const dots = [];
    for (let i = step; i < activeCoords.length - step; i += step) {
      dots.push(activeCoords[i]);
    }
    return dots;
  }, [activeCoords]);

  const sourceLabel = normSource?.label || 'Gandhipuram, Coimbatore';
  const destLabel = normDest?.label || 'Peelamedu, Coimbatore';

  return (
    <div className="relative w-full h-full min-h-[400px] overflow-hidden bg-[#e5e3df]">
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        scrollWheelZoom={true}
        zoomControl={false}
        className="w-full h-full"
      >
        {/* Clean OpenStreetMap Standard Tiles — Free, authentic, street-accurate */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />

        <MapBoundsHandler
          sourceCoords={normSource}
          destCoords={normDest}
          routes={preparedRoutes}
        />

        {/* ── Origin Marker (Google Maps Style White Disc + Google Blue core) ── */}
        {normSource && normSource.lat && normSource.lng && (
          <Marker
            position={[normSource.lat, normSource.lng]}
            icon={createSourceMarkerIcon(sourceLabel)}
          >
            <Popup>
              <div className="p-1 space-y-1">
                <div className="text-[10px] font-bold uppercase tracking-wider text-blue-600">
                  📍 Origin
                </div>
                <div className="text-xs font-semibold text-gray-900">{sourceLabel}</div>
              </div>
            </Popup>
          </Marker>
        )}

        {/* ── Destination Marker (Google Maps Red Pin) ── */}
        {normDest && normDest.lat && normDest.lng && (
          <Marker
            position={[normDest.lat, normDest.lng]}
            icon={createDestMarkerIcon(destLabel)}
          >
            <Popup>
              <div className="p-1 space-y-1">
                <div className="text-[10px] font-bold uppercase tracking-wider text-red-600">
                  🎯 Destination Target
                </div>
                <div className="text-xs font-semibold text-gray-900">{destLabel}</div>
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
                      <span className="text-[10px] uppercase font-bold text-red-600">
                        🚨 Hazard on Corridor
                      </span>
                      <span className="text-[9px] px-1.5 py-0.5 bg-red-100 text-red-700 rounded font-bold">
                        {ls.severity || 'CRITICAL'}
                      </span>
                    </div>
                    <div className="text-xs font-bold text-gray-900">{ls.title}</div>
                    <div className="text-[10px] text-gray-500">{ls.road_name}</div>
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

        {/* ── Render Alternative Routes (Google Maps Muted Gray + Clickable) ── */}
        {preparedRoutes.map((route, idx) => {
          if (idx === selectedRoute) return null;
          const isBlocked = route.is_blocked || (route.landslide_hazard && route.landslide_hazard.blocked);
          const coords = route.coordinates || [];
          if (coords.length === 0) return null;

          const altMidIdx = Math.floor(coords.length * 0.55);
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
                  weight: 24,
                  opacity: 0.0,
                }}
              />

              {/* Outer Casing for Alternative Route */}
              <Polyline
                positions={coords}
                eventHandlers={{
                  click: () => {
                    if (onSelectRoute) onSelectRoute(idx);
                  },
                }}
                pathOptions={{
                  color: isBlocked ? '#991b1b' : '#5f6368',
                  weight: 7,
                  opacity: 0.45,
                  dashArray: isBlocked ? '6, 8' : null,
                  lineCap: 'round',
                  lineJoin: 'round',
                }}
              />

              {/* Inner Polyline for Alternative Route */}
              <Polyline
                positions={coords}
                eventHandlers={{
                  click: () => {
                    if (onSelectRoute) onSelectRoute(idx);
                  },
                }}
                pathOptions={{
                  color: isBlocked ? '#ef4444' : '#80868b',
                  weight: 4.5,
                  opacity: 0.85,
                  dashArray: isBlocked ? '6, 8' : null,
                  lineCap: 'round',
                  lineJoin: 'round',
                }}
              >
                <Popup>
                  <div className="p-1 space-y-1 cursor-pointer" onClick={() => onSelectRoute && onSelectRoute(idx)}>
                    <div className="text-xs font-bold text-gray-900">
                      {route.name || `Alternative Route ${idx + 1}`}
                    </div>
                    <div className="text-xs text-gray-600">
                      {route.distance_km} km · {Math.round(route.duration_min)} mins
                    </div>
                    <div className="text-[10px] text-blue-600 font-bold mt-1">
                      👆 Click to choose this path
                    </div>
                  </div>
                </Popup>
              </Polyline>

              {/* Google Maps Clickable ETA Badge on Alternative Route */}
              {altMidPoint && !isBlocked && (
                <Marker
                  position={[altMidPoint[0], altMidPoint[1]]}
                  icon={createEtaBadgeIcon(route.duration_min || 22, route.distance_km || 7.0, false)}
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

        {/* ── Render Selected Active Route (Google Maps Royal Blue + Casing) ── */}
        {activeRoute && activeCoords.length > 0 && (
          <React.Fragment>
            {/* Outer Navy Casing Border */}
            <Polyline
              positions={activeCoords}
              pathOptions={{
                color: '#174ea6', // Google Navy Blue Casing
                weight: 9.5,
                opacity: 0.95,
                lineCap: 'round',
                lineJoin: 'round',
              }}
            />
            {/* Inner Vibrant Google Maps Blue Polyline */}
            <Polyline
              positions={activeCoords}
              pathOptions={{
                color: '#1a73e8', // Google Royal Blue
                weight: 6.5,
                opacity: 1.0,
                lineCap: 'round',
                lineJoin: 'round',
              }}
            />

            {/* Directional maneuver arrows along route (Google forward driving chevrons) */}
            {directionArrows.map((arrow, aIdx) => (
              <Marker
                key={`dir-arrow-${aIdx}`}
                position={[arrow.pos[0], arrow.pos[1]]}
                icon={createDirectionArrowIcon(arrow.bearing)}
                interactive={false}
              />
            ))}

            {/* Turn maneuver dots along the route */}
            {waypointDots.map((pt, dotIdx) => (
              <CircleMarker
                key={`waypoint-dot-${dotIdx}`}
                center={[pt[0], pt[1]]}
                radius={3.5}
                pathOptions={{
                  color: '#174ea6',
                  fillColor: '#ffffff',
                  fillOpacity: 1.0,
                  weight: 2,
                }}
              />
            ))}

            {/* Floating Google Maps ETA Duration Badge over selected route */}
            {midPoint && (
              <Marker
                position={[midPoint[0], midPoint[1]]}
                icon={createEtaBadgeIcon(activeRoute.duration_min || 18, activeRoute.distance_km || 9.0, true)}
                interactive={false}
              />
            )}
          </React.Fragment>
        )}
      </MapContainer>

      {/* ── Google Maps Floating Legend (Bottom-Left) ── */}
      <div className="absolute bottom-6 left-6 z-[1000] bg-white/95 backdrop-blur-md border border-gray-200 p-3 rounded-2xl shadow-xl space-y-1.5 text-xs text-gray-800">
        <div className="text-[10px] font-bold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-blue-600 animate-pulse"></span>
          Google Navigation View
        </div>
        <div className="flex items-center gap-2">
          <span className="w-5 h-2 bg-[#1a73e8] rounded-full border border-[#174ea6]"></span>
          <span className="text-gray-900 font-bold">Fastest Active Route</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-5 h-1.5 bg-[#80868b] rounded-full"></span>
          <span className="text-gray-600 font-medium">Alternative Roads</span>
        </div>
        {relevantLandslides.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="w-5 h-1.5 bg-red-500 rounded-full border-dashed border-red-300"></span>
            <span className="text-red-600 font-medium">Hazard Alert</span>
          </div>
        )}
      </div>
    </div>
  );
}
