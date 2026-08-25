import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';

// Create custom colored SVG pin icons for Leaflet
const createCustomIcon = (colorHex, label) => {
  return L.divIcon({
    className: 'custom-leaflet-marker',
    html: `
      <div style="
        position: relative;
        width: 34px;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.4));
      ">
        <svg width="34" height="42" viewBox="0 0 34 42" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M17 0C7.61116 0 0 7.61116 0 17C0 29.75 17 42 17 42C17 42 34 29.75 34 17C34 7.61116 26.3888 0 17 0Z" fill="${colorHex}"/>
          <circle cx="17" cy="17" r="8" fill="#FFFFFF"/>
          <circle cx="17" cy="17" r="4.5" fill="${colorHex}"/>
        </svg>
        <span style="
          position: absolute;
          top: -20px;
          background: #0f172a;
          color: #f8fafc;
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 600;
          border: 1px solid ${colorHex};
          white-space: nowrap;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        ">${label}</span>
      </div>
    `,
    iconSize: [34, 42],
    iconAnchor: [17, 42],
    popupAnchor: [0, -42],
  });
};

// Red Pulsing Beacon for Active Landslides
const createLandslideIcon = (severity) => {
  return L.divIcon({
    className: 'custom-landslide-marker',
    html: `
      <div style="
        position: relative;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
      ">
        <span style="
          position: absolute;
          width: 36px;
          height: 36px;
          background: rgba(239, 68, 68, 0.4);
          border-radius: 50%;
          animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
        "></span>
        <div style="
          position: relative;
          width: 28px;
          height: 28px;
          background: #dc2626;
          border: 2px solid #ffffff;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 8px rgba(0,0,0,0.5);
          color: #ffffff;
          font-weight: bold;
          font-size: 14px;
        ">
          ⚠️
        </div>
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -18],
  });
};

const greenSourceIcon = createCustomIcon('#10b981', 'SOURCE');
const redDestIcon = createCustomIcon('#ef4444', 'DESTINATION');

// Helper component to auto-fit map view
function MapBoundsHandler({ sourceCoords, destCoords, routes, landslides }) {
  const map = useMap();

  useEffect(() => {
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

    if (landslides && landslides.length > 0) {
      landslides.forEach((ls) => {
        if (ls.lat && ls.lng) {
          points.push([ls.lat, ls.lng]);
        }
      });
    }

    if (points.length === 1) {
      map.setView(points[0], 14, { animate: true });
    } else if (points.length > 1) {
      const bounds = L.latLngBounds(points);
      map.fitBounds(bounds, { padding: [60, 60], maxZoom: 15, animate: true });
    }
  }, [sourceCoords, destCoords, routes, landslides, map]);

  return null;
}

export default function MapView({
  sourceCoords,
  destCoords,
  routes = [],
  landslides = [],
  selectedRoute = 0,
  onSelectRoute,
}) {
  const defaultCenter = [11.0168, 76.9558];
  const defaultZoom = 13;

  return (
    <div className="relative w-full h-full min-h-[400px] rounded-xl overflow-hidden shadow-2xl border border-slate-800 bg-slate-950">
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />

        <MapBoundsHandler
          sourceCoords={sourceCoords}
          destCoords={destCoords}
          routes={routes}
          landslides={landslides}
        />

        {/* Source Marker (Green) */}
        {sourceCoords && sourceCoords.lat && sourceCoords.lng && (
          <Marker
            position={[sourceCoords.lat, sourceCoords.lng]}
            icon={greenSourceIcon}
          >
            <Popup>
              <div className="p-1 space-y-1">
                <div className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                  📍 Origin Location
                </div>
                <div className="text-sm font-semibold text-slate-100">
                  {sourceCoords.label || 'Selected Origin'}
                </div>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Destination Marker (Red) */}
        {destCoords && destCoords.lat && destCoords.lng && (
          <Marker
            position={[destCoords.lat, destCoords.lng]}
            icon={redDestIcon}
          >
            <Popup>
              <div className="p-1 space-y-1">
                <div className="text-xs font-bold uppercase tracking-wider text-rose-400">
                  🎯 Destination Target
                </div>
                <div className="text-sm font-semibold text-slate-100">
                  {destCoords.label || 'Selected Destination'}
                </div>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Active Landslide Hazard Beacons & Radii */}
        {landslides.map((ls, idx) => {
          const lsLat = ls.lat || ls.location?.coordinates?.[1];
          const lsLng = ls.lng || ls.location?.coordinates?.[0];
          if (!lsLat || !lsLng) return null;

          return (
            <React.Fragment key={`landslide-${idx}`}>
              <Marker
                position={[lsLat, lsLng]}
                icon={createLandslideIcon(ls.severity)}
              >
                <Popup>
                  <div className="p-1 space-y-1.5 min-w-[200px]">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] uppercase font-bold text-red-400 flex items-center gap-1">
                        🚨 Active Hazard
                      </span>
                      <span className="text-[9px] px-1.5 py-0.5 bg-red-500/20 text-red-300 rounded font-bold">
                        {ls.severity || 'CRITICAL'}
                      </span>
                    </div>
                    <div className="text-xs font-bold text-slate-100">{ls.title}</div>
                    <div className="text-[11px] text-slate-400">
                      {ls.region_name} · {ls.road_name}
                    </div>
                    <div className="text-[10px] text-red-300 bg-red-950/60 p-1 rounded border border-red-500/30">
                      Blockage Radius: {ls.radius_m || 2500}m
                    </div>
                  </div>
                </Popup>
              </Marker>
              <Circle
                center={[lsLat, lsLng]}
                radius={ls.radius_m || 2500}
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

        {/* Render Routes as Polylines */}
        {routes.map((route, idx) => {
          const isBlocked = route.is_blocked || (route.landslide_hazard && route.landslide_hazard.blocked);
          const isSelected = idx === selectedRoute;
          const coords = route.coordinates || [];

          let color = isSelected ? '#2563eb' : '#94a3b8';
          let weight = isSelected ? 6 : 4;
          let opacity = isSelected ? 0.95 : 0.65;
          let dashArray = isSelected ? null : '8, 8';

          if (isBlocked) {
            color = '#ef4444'; // Red for blocked route
            weight = isSelected ? 6 : 4;
            dashArray = '4, 6';
          }

          return (
            <Polyline
              key={`route-poly-${idx}`}
              positions={coords}
              eventHandlers={{
                click: () => {
                  if (!isBlocked && onSelectRoute) {
                    onSelectRoute(idx);
                  }
                },
              }}
              pathOptions={{
                color: color,
                weight: weight,
                opacity: opacity,
                dashArray: dashArray,
              }}
            >
              <Popup>
                <div className="p-1 space-y-1">
                  <div className="flex items-center justify-between gap-2">
                    <div className="text-xs font-bold text-slate-100">
                      {route.name || `Route Option ${idx + 1}`}
                    </div>
                    {isBlocked ? (
                      <span className="text-[10px] px-1.5 py-0.5 bg-red-500/20 text-red-300 font-bold rounded">
                        BLOCKED
                      </span>
                    ) : isSelected ? (
                      <span className="text-[10px] px-1.5 py-0.5 bg-blue-500/20 text-blue-300 font-semibold rounded">
                        Active Safe Route
                      </span>
                    ) : null}
                  </div>
                  <div className="text-xs text-slate-400">
                    Distance: <span className="text-slate-200 font-medium">{route.distance_km} km</span> · Duration: <span className="text-slate-200 font-medium">{Math.round(route.duration_min)} mins</span>
                  </div>
                </div>
              </Popup>
            </Polyline>
          );
        })}
      </MapContainer>

      {/* Map Floating Legend */}
      <div className="absolute top-4 right-4 z-[1000] bg-slate-900/90 backdrop-blur border border-slate-800 p-2.5 rounded-lg shadow-lg space-y-1.5 text-xs">
        <div className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
          Route Map Legend
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-1 bg-blue-600 rounded"></span>
          <span className="text-slate-200">Recommended Safe Route</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-0.5 border-t-2 border-dashed border-slate-400"></span>
          <span className="text-slate-400">Alternative Options</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-1 bg-red-500 rounded border-dashed border-red-300"></span>
          <span className="text-red-400 font-medium">Blocked Road / Hazard</span>
        </div>
      </div>
    </div>
  );
}
