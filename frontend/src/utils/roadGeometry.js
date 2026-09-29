import axios from 'axios';
import corridorGeometries from '../data/corridor_geometries.json';

function coordDist(lat1, lng1, lat2, lng2) {
  return Math.sqrt((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2);
}

export function getPresetCorridorGeometry(sLat, sLng, dLat, dLng) {
  if (!sLat || !sLng || !dLat || !dLng) return null;

  const presets = [
    { key: 'gandhipuram-airport', s: [11.0168, 76.9558], d: [11.0324, 77.0411] },
    { key: 'rspuram-junction', s: [11.0094, 76.9458], d: [10.9980, 76.9634] },
    { key: 'peelamedu-ukkadam', s: [11.0244, 77.0028], d: [10.9892, 76.9613] },
    { key: 'saravanampatti-singanallur', s: [11.0805, 76.9959], d: [10.9995, 77.0267] },
  ];

  for (const p of presets) {
    const dS = coordDist(sLat, sLng, p.s[0], p.s[1]);
    const dD = coordDist(dLat, dLng, p.d[0], p.d[1]);
    if (dS < 0.025 && dD < 0.025) {
      const geo = corridorGeometries[p.key];
      if (geo) {
        return {
          primaryCoords: geo.primary?.coords || [],
          altCoords: geo.alt?.coords || [],
        };
      }
    }
  }
  return null;
}

export async function fetchRoadCoordinates(sLat, sLng, dLat, dLng) {
  if (!sLat || !sLng || !dLat || !dLng) {
    return { primary: [], alternative: [] };
  }

  const presetMatch = getPresetCorridorGeometry(sLat, sLng, dLat, dLng);
  if (presetMatch && presetMatch.primaryCoords.length > 20) {
    return {
      primary: presetMatch.primaryCoords,
      alternative: presetMatch.altCoords.length > 20 ? presetMatch.altCoords : presetMatch.primaryCoords,
    };
  }

  const osrmEndpoints = [
    'https://routing.openstreetmap.de/routed-car/route/v1/driving',
    'https://router.project-osrm.org/route/v1/driving',
  ];

  for (const base of osrmEndpoints) {
    try {
      const url = ${base}/,;,?overview=full&geometries=geojson&alternatives=true;
      const res = await axios.get(url, { timeout: 6000 });
      const routes = res.data?.routes || [];

      if (routes.length >= 2) {
        const pCoords = routes[0].geometry.coordinates.map((c) => [c[1], c[0]]);
        const aCoords = routes[1].geometry.coordinates.map((c) => [c[1], c[0]]);
        return { primary: pCoords, alternative: aCoords };
      }

      if (routes.length === 1) {
        const pCoords = routes[0].geometry.coordinates.map((c) => [c[1], c[0]]);

        const dlat = dLat - sLat;
        const dlng = dLng - sLng;
        const rlen = Math.sqrt(dlat * dlat + dlng * dlng) || 1e-5;
        const perpLat = -dlng / rlen;
        const perpLng = dlat / rlen;
        const wpLat = sLat + 0.5 * dlat + perpLat * 0.25 * rlen;
        const wpLng = sLng + 0.5 * dlng + perpLng * 0.25 * rlen;

        try {
          const wpUrl = ${base}/,;,;,?overview=full&geometries=geojson;
          const wpRes = await axios.get(wpUrl, { timeout: 4500 });
          const wpRoutes = wpRes.data?.routes || [];
          if (wpRoutes.length > 0) {
            const aCoords = wpRoutes[0].geometry.coordinates.map((c) => [c[1], c[0]]);
            return { primary: pCoords, alternative: aCoords };
          }
        } catch {
        }

        return { primary: pCoords, alternative: pCoords };
      }
    } catch {
    }
  }

  const steps = 30;
  const primaryFallback = [];
  const altFallback = [];
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const baseLat = sLat + (dLat - sLat) * t;
    const baseLng = sLng + (dLng - sLng) * t;
    const curve = Math.sin(t * Math.PI);
    primaryFallback.push([Number((baseLat + curve * 0.005).toFixed(5)), Number((baseLng - curve * 0.004).toFixed(5))]);
    altFallback.push([Number((baseLat - curve * 0.008).toFixed(5)), Number((baseLng + curve * 0.009).toFixed(5))]);
  }

  return { primary: primaryFallback, alternative: altFallback };
}
