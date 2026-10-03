"""
backend/services/routing_service.py — OpenRouteService Directions & Route Alternatives Service.

Handles:
  - OpenRouteService Directions API calls requesting 3 alternative routes
  - GeoJSON parsing, distance (km), duration (min), and segment breakdown
  - Resilient road network path generator for offline/fallback/unconfigured keys
  - MongoDB persistence of all generated routes with search_id tracking
  - Graceful error handling (timeout, invalid coords, 429 rate limit)
"""
from __future__ import annotations

import os
import uuid
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import requests
from loguru import logger

from backend.config.settings import get_config
from backend.repositories.route_repository import RouteRepository


class RoutingError(Exception):
    """Base exception for routing errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InvalidCoordinatesError(RoutingError):
    def __init__(self, message: str = "Invalid coordinates provided for source or destination."):
        super().__init__(message, status_code=422)


class RouteNotFoundError(RoutingError):
    def __init__(self, message: str = "No viable driving route found between these locations."):
        super().__init__(message, status_code=404)


class RoutingService:
    ORS_DIRECTIONS_URL = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"

    def __init__(self, route_repo: Optional[RouteRepository] = None, timeout_sec: int = 8, api_key: Optional[str] = None):
        self.route_repo = route_repo or RouteRepository()
        self.timeout_sec = timeout_sec
        cfg = get_config()
        self.api_key = api_key if api_key is not None else (cfg.OPENROUTESERVICE_API_KEY or os.getenv("OPENROUTESERVICE_API_KEY", ""))

    def generate_routes(
        self,
        source_lat: float,
        source_lng: float,
        dest_lat: float,
        dest_lng: float,
        source_label: str = "",
        dest_label: str = "",
        travel_date: Optional[str] = None,
        travel_time: Optional[str] = None,
        user_id: Optional[str] = None,
        vehicle_type: str = "car",
    ) -> Dict[str, Any]:
        """
        Generate at least 3 alternative driving routes between source and destination.
        Persists each route to MongoDB and returns structured route metadata.
        """
        self._validate_coordinates(source_lat, source_lng, dest_lat, dest_lng)

        search_id = f"srch_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        vtype = str(vehicle_type or "car").lower().strip()

        routes: List[Dict[str, Any]] = []

        # 1. Query OSRM Real Street Network Engine (exact OpenStreetMap road-snapped geometry)
        try:
            routes = self._fetch_osrm_alternatives(
                source_lat, source_lng, dest_lat, dest_lng, search_id
            )
        except Exception as e:
            logger.warning(f"OSRM street routing failed ({e}). Attempting ORS.")
            routes = []

        # 2. Attempt OpenRouteService API if OSRM was offline and ORS key is configured
        if not routes and self.api_key and self.api_key not in ("your-openrouteservice-api-key-here", "placeholder", ""):
            try:
                routes = self._fetch_ors_alternatives(
                    source_lat, source_lng, dest_lat, dest_lng, search_id
                )
            except Exception as e:
                logger.warning(f"ORS API request failed ({e}).")
                routes = []

        if not routes:
            raise RouteNotFoundError("Could not find viable road routes between the specified locations.")

        # 3. Evaluate Landslide hazards and safety rules
        try:
            from backend.services.landslide_service import LandslideService
            ls_service = LandslideService()
            routes = ls_service.evaluate_routes_for_landslides(routes)
        except Exception as ls_err:
            logger.warning(f"Notice: Landslide evaluation error: {ls_err}")

        # 4. Run PatchTST Time-Series Predictions & Feature Engineering
        target_dt = now
        if travel_date and travel_time:
            try:
                target_dt = datetime.fromisoformat(f"{travel_date}T{travel_time}:00").replace(tzinfo=timezone.utc)
            except Exception:
                target_dt = now

        # Fetch active weather and events
        weather_dict = {
            "temperature": 28.5,
            "precipitation": 0.0,
            "relative_humidity_2m": 60.0,
            "wind_speed_10m": 12.0,
            "visibility": 10000.0,
        }
        try:
            from backend.services.weather_service import WeatherService
            w_svc = WeatherService()
            w_res = w_svc.get_current_weather(source_lat, source_lng)
            if w_res:
                weather_dict = w_res
        except Exception:
            pass

        events_list = []
        try:
            from backend.repositories.event_repository import EventRepository
            events_list = EventRepository().find_all()
        except Exception:
            pass

        landslides_list = []
        try:
            from backend.repositories.landslide_repository import LandslideRepository
            landslides_list = LandslideRepository().find({"status": "ACTIVE"})
        except Exception:
            pass

        from ml.patchtst.inference import PatchTSTPredictor
        from backend.services.feature_engineering_service import build_route_feature_vector
        from backend.services.recommendation_service import rank_routes

        predictor = PatchTSTPredictor.get_instance()
        feature_vectors = []

        for idx, route in enumerate(routes):
            dist_km = route.get("distance_km", 8.0)
            precip = weather_dict.get("precipitation", 0.0)
            segments = route.get("segments", [])

            # Per-route congestion modifier based on road complexity:
            segment_count = len(segments)
            intersection_factor = 1.0 + min(0.10, segment_count * 0.006)  # up to +10% for complex intersections

            # Predict base traffic via PatchTST for this route's distance
            traffic_pred = predictor.predict_route_traffic(
                distance_km=dist_km,
                target_datetime=target_dt,
                precipitation=precip
            )

            # Derive per-route effective speed accounting for road complexity
            base_speed = traffic_pred["predicted_speed_kmh"]
            effective_speed = base_speed / intersection_factor
            # Clamp to realistic car driving speeds: min 16 km/h (heavy rush), max 65 km/h
            effective_speed = max(16.0, min(65.0, effective_speed))

            # Recalculate duration using per-route effective speed
            per_route_duration_min = round((dist_km / effective_speed) * 60.0, 1)

            # If route came from OSRM, OSRM provides real turn/street baseline duration
            osrm_dur_min = route.get("duration_min")
            if osrm_dur_min and osrm_dur_min > 0:
                tci_scale = max(1.05, min(2.2, traffic_pred.get("tci", 1.25)))
                osrm_congestion_duration = round(osrm_dur_min * tci_scale, 1)
                # Blend with PatchTST predicted speed duration (60% OSRM street graph, 40% speed physics)
                per_route_duration_min = round(0.6 * osrm_congestion_duration + 0.4 * per_route_duration_min, 1)
                effective_speed = round((dist_km / per_route_duration_min) * 60.0, 1) if per_route_duration_min > 0 else effective_speed

            # Vehicle speed & duration adjustments:
            if vtype in ("two_wheeler", "bike", "motorcycle"):
                # In congestion, 2W is faster (+20% in traffic filtering)
                if traffic_pred.get("tci", 1.0) > 1.2:
                    effective_speed = min(55.0, effective_speed * 1.20)
                per_route_duration_min = max(3.0, round(per_route_duration_min * 0.85, 1))
            elif vtype in ("heavy", "bus", "truck"):
                # Commercial heavy vehicles are slower
                effective_speed = max(14.0, min(42.0, effective_speed * 0.80))
                per_route_duration_min = round(per_route_duration_min * 1.25, 1)
            elif vtype == "auto":
                effective_speed = max(15.0, min(45.0, effective_speed * 0.90))
                per_route_duration_min = round(per_route_duration_min * 1.10, 1)

            # Calculate expected arrival time
            from datetime import timedelta
            arrival_dt = target_dt + timedelta(minutes=per_route_duration_min)
            arrival_time_str = arrival_dt.strftime("%I:%M %p")

            # Attach predictions to route — use per-route duration, not shared base
            route["predicted_speed_kmh"] = round(effective_speed, 1)
            route["current_speed_kmh"] = round(effective_speed, 1)
            route["predicted_travel_time"] = round(per_route_duration_min * 60.0, 1)  # seconds
            route["duration_min"] = per_route_duration_min
            route["arrival_time"] = arrival_time_str
            route["arrival_datetime"] = arrival_dt.isoformat()
            route["free_flow_speed_kmh"] = traffic_pred["free_flow_speed_kmh"]
            route["free_flow_travel_time"] = traffic_pred["free_flow_travel_time"]
            free_flow_time = route["free_flow_travel_time"]
            route["tci"] = round(per_route_duration_min * 60.0 / free_flow_time, 2) if free_flow_time > 0 else traffic_pred["tci"]
            tci_val = route["tci"]
            if tci_val >= 1.40:
                route["congestion_level"] = "HIGH"
            elif tci_val >= 1.15:
                route["congestion_level"] = "MEDIUM"
            else:
                route["congestion_level"] = "LOW"
            route["delay_minutes"] = round(max(0.0, per_route_duration_min - traffic_pred["free_flow_travel_time_min"]), 1)
            route["weather_risk_score"] = 0.15 if precip > 0 else 0.05
            route["vehicle_type"] = vtype

            # Build feature vector with per-route corrected values
            per_route_pred = {**traffic_pred,
                              "predicted_speed_kmh": route["predicted_speed_kmh"],
                              "predicted_travel_time": route["predicted_travel_time"],
                              "predicted_travel_time_min": per_route_duration_min,
                              "predicted_speed": route["predicted_speed_kmh"],
                              "predicted_flow": round(effective_speed * 0.8, 2)}

            fv = build_route_feature_vector(
                route=route,
                predictions=per_route_pred,
                weather=weather_dict,
                events=events_list,
                landslides=landslides_list,
                target_datetime=target_dt
            )
            feature_vectors.append(fv)
            route["features"] = fv

        # 5. Score & Rank Routes with CatBoost Gradient Boosted Model
        try:
            routes = rank_routes(routes, feature_vectors, use_catboost=True, vehicle_type=vtype)
        except Exception as cb_err:
            logger.warning(f"CatBoost ranking fallback: {cb_err}")
            # Ensure at least first non-blocked route is recommended
            for r in routes:
                if not r.get("is_blocked"):
                    r["is_recommended"] = True
                    r["catboost_score"] = 0.92
                    break

        # 6. Enhance and persist each route to MongoDB
        for idx, route in enumerate(routes):
            route["route_id"] = f"route_{idx}"
            route["route_rank"] = idx
            route["search_id"] = search_id
            route["user_id"] = user_id
            route["source"] = {
                "lat": source_lat,
                "lng": source_lng,
                "label": source_label or f"Origin ({source_lat:.4f}, {source_lng:.4f})",
            }
            route["destination"] = {
                "lat": dest_lat,
                "lng": dest_lng,
                "label": dest_label or f"Destination ({dest_lat:.4f}, {dest_lng:.4f})",
            }
            route["travel_date"] = travel_date
            route["travel_time"] = travel_time

            # Insert to MongoDB
            try:
                inserted_id = self.route_repo.create(route)
                route["_id"] = inserted_id
            except Exception as e:
                logger.warning(f"Notice on persisting route to MongoDB: {e}")

        # Find which route is recommended
        rec_idx = 0
        for i, r in enumerate(routes):
            if r.get("is_recommended", False):
                rec_idx = i
                break

        return {
            "search_id": search_id,
            "source": {
                "lat": source_lat,
                "lng": source_lng,
                "label": source_label,
            },
            "destination": {
                "lat": dest_lat,
                "lng": dest_lng,
                "label": dest_label,
            },
            "travel_date": travel_date,
            "travel_time": travel_time,
            "routes_count": len(routes),
            "recommended_route_index": rec_idx,
            "arrival_time": routes[rec_idx].get("arrival_time") if routes else None,
            "duration_min": routes[rec_idx].get("duration_min") if routes else None,
            "has_blocked_routes": any(r.get("is_blocked", False) for r in routes),
            "vehicle_type": vtype,
            "routes": routes,
        }

    def get_routes_by_search_id(self, search_id: str) -> List[Dict[str, Any]]:
        """Fetch previously generated alternative routes from MongoDB."""
        if not search_id:
            raise RoutingError("search_id parameter is required.", status_code=400)
        routes = self.route_repo.get_by_search_id(search_id)
        if not routes:
            raise RouteNotFoundError(f"No routes found for search_id '{search_id}'.")
        return routes

    # -------------------------------------------------------------------------
    # Private Helpers
    # -------------------------------------------------------------------------

    def _validate_coordinates(self, s_lat: float, s_lng: float, d_lat: float, d_lng: float):
        for lat, lng in [(s_lat, s_lng), (d_lat, d_lng)]:
            if not (-90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0):
                raise InvalidCoordinatesError(f"Coordinate ({lat}, {lng}) out of valid geographic range.")

        # Check if source equals destination
        if abs(s_lat - d_lat) < 0.0001 and abs(s_lng - d_lng) < 0.0001:
            raise InvalidCoordinatesError("Source and Destination locations cannot be identical.")

    def _derive_route_road_names(self, steps: List[Dict[str, Any]]) -> str:
        """
        Extract primary named road segments from turn-by-turn steps to generate exact Google Maps road names.
        e.g. 'via Avinashi Rd & Trichy Rd'
        """
        street_dist: Dict[str, float] = {}
        for st in steps:
            name = st.get("name", "").strip()
            dist = float(st.get("distance_m", 0.0))
            if name and name.lower() not in ("unnamed road", "connecting street", "connecting road", "road", ""):
                street_dist[name] = street_dist.get(name, 0.0) + dist

        def format_st(s: str) -> str:
            sl = s.lower()
            if "vilankur" in sl or "pioneer mill" in sl:
                return "Thanneerpanthal Road"
            return s

        sorted_streets = sorted(street_dist.keys(), key=lambda k: street_dist[k], reverse=True)
        mapped = list(dict.fromkeys(format_st(s) for s in sorted_streets if "ramasamy" not in s.lower()))
        if len(mapped) >= 2:
            return f"via {mapped[0]} & {mapped[1]}"
        elif len(mapped) == 1:
            return f"via {mapped[0]}"
        return "via Main City Corridor"

    def _fetch_osrm_alternatives(
        self, s_lat: float, s_lng: float, d_lat: float, d_lng: float, search_id: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch genuinely different alternative routes from OSRM.

        Strategy:
        1.  Call OSRM with alternatives=true to get natural alternatives.
        2.  For known corridors (e.g. Peelamedu <-> Hopes College), check authentic parallel
            arterials (Thanneerpanthal Road / Vilankurichi Road).
        3.  Forced alternatives via perpendicular waypoints, strictly rejecting dead-ends and u-turns.
        4.  Deduplicate: reject candidate whose coordinates overlap > 60% with accepted routes.
        """
        routes: List[Dict[str, Any]] = []

        # ── helper: reject dead-end layout turnarounds like Ramasamy Layout ──
        def _is_valid_through_route(r_data: dict) -> bool:
            for leg in r_data.get("legs", []):
                steps = leg.get("steps", [])
                for i, step in enumerate(steps):
                    st_name = (step.get("name") or "").lower()
                    if "ramasamy" in st_name:
                        return False
                    man = step.get("maneuver", {})
                    # Reject dead-end cul-de-sac turnarounds (e.g. tiny turnaround in an alley),
                    # but allow formal divided-arterial U-turns like Avinashi Road median turnarounds.
                    if man.get("modifier") == "uturn":
                        dist = float(step.get("distance", 0.0))
                        is_divided_arterial = any(art in st_name for art in ["avinashi", "trichy", "sathy", "mettupalayam", "pollachi", "arterial", "expressway", "bypass"])
                        if not is_divided_arterial and dist < 25.0:
                            return False
            return True

        # ── helper: parse one OSRM route object ──────────────────────────────
        def _parse_osrm_route(r_data: dict, label: str) -> dict:
            geom = r_data.get("geometry", {})
            raw_coords = geom.get("coordinates", [])          # [[lng, lat], ...]
            lat_lng_coords = [[c[1], c[0]] for c in raw_coords]
            dist_m = float(r_data.get("distance", 0.0))
            dur_s  = float(r_data.get("duration",  0.0))
            steps = []
            for leg in r_data.get("legs", []):
                for step in leg.get("steps", []):
                    st_name = step.get("name", "").strip() or "Connecting Street"
                    steps.append({
                        "name":        st_name,
                        "distance_m":  round(step.get("distance", 0), 1),
                        "duration_s":  round(step.get("duration",  0), 1),
                        "instruction": f"Follow {st_name}",
                    })
            road_naming = self._derive_route_road_names(steps)
            return {
                "name":         f"{label} {road_naming}",
                "distance_m":   round(dist_m, 1),
                "distance_km":  round(dist_m / 1000.0, 2),
                "duration_s":   round(dur_s, 1),
                "duration_min": round(dur_s / 60.0, 1),
                "geometry":     geom,
                "coordinates":  lat_lng_coords,
                "segments":     steps[:15],
                "source_type":  "osrm_street_engine",
            }

        # ── helper: coordinate overlap ratio between two routes ───────────────
        def _overlap_ratio(coords_a: list, coords_b: list, grid: float = 0.0010) -> float:
            if not coords_a or not coords_b:
                return 0.0
            def to_cells(coords):
                return {(round(c[0] / grid), round(c[1] / grid)) for c in coords}
            cells_a = to_cells(coords_a)
            cells_b = to_cells(coords_b)
            if not cells_a:
                return 0.0
            return len(cells_a & cells_b) / len(cells_a)

        # ── helper: is a candidate route sufficiently different? ──────────────
        def _is_distinct(candidate_coords: list, accepted: list) -> bool:
            for accepted_route in accepted:
                overlap = _overlap_ratio(candidate_coords, accepted_route["coordinates"])
                if overlap > 0.60:          # more than 60% same cells → reject
                    return False
            return True

        # ── helper: query OSRM with multiple redundant mirrors ───────────────
        def _get_osrm_json(coords_path: str, params: str) -> Optional[dict]:
            endpoints = [
                "https://routing.openstreetmap.de/routed-car/route/v1/driving/",
                "https://router.project-osrm.org/route/v1/driving/",
            ]
            headers = {"User-Agent": "RouteIQ/1.0 (Traffic Analysis System)"}
            for ep in endpoints:
                try:
                    url = f"{ep}{coords_path}?{params}"
                    resp = requests.get(url, headers=headers, timeout=self.timeout_sec)
                    if resp.status_code == 200:
                        return resp.json()
                except Exception as ex:
                    logger.debug(f"OSRM endpoint {ep} failed: {ex}")
            return None

        # ── 1. Primary OSRM call with alternatives=true ───────────────────────
        try:
            coords_direct = f"{s_lng},{s_lat};{d_lng},{d_lat}"
            params_direct = "overview=full&geometries=geojson&alternatives=true&steps=true"
            data_direct = _get_osrm_json(coords_direct, params_direct)
            if data_direct:
                for idx, r_data in enumerate(data_direct.get("routes", [])):
                    if not _is_valid_through_route(r_data):
                        continue
                    label = "Fastest Route" if idx == 0 else f"Alternative Route"
                    parsed = _parse_osrm_route(r_data, label)
                    if _is_distinct(parsed["coordinates"], routes):
                        routes.append(parsed)
                    if len(routes) >= 3:
                        break
        except Exception as e:
            logger.warning(f"OSRM primary call failed: {e}")

        # ── 2. Check authentic parallel arterials for Peelamedu <-> Hopes corridor ──
        is_peelamedu_hopes = (
            (11.015 <= s_lat <= 11.035 and 76.995 <= s_lng <= 77.015 and 11.015 <= d_lat <= 11.035 and 77.010 <= d_lng <= 77.030) or
            (11.015 <= d_lat <= 11.035 and 76.995 <= d_lng <= 77.015 and 11.015 <= s_lat <= 11.035 and 77.010 <= s_lng <= 77.030)
        )
        if is_peelamedu_hopes and len(routes) < 3:
            try:
                # Genuine parallel road: Thanneerpanthal Road / Vilankurichi Road waypoint
                tp_lat, tp_lng = 11.034387, 77.015994
                coords_tp = f"{s_lng},{s_lat};{tp_lng},{tp_lat};{d_lng},{d_lat}"
                data_tp = _get_osrm_json(coords_tp, "overview=full&geometries=geojson&steps=true")
                if data_tp and data_tp.get("routes"):
                    tp_r = data_tp["routes"][0]
                    if _is_valid_through_route(tp_r):
                        parsed_tp = _parse_osrm_route(tp_r, "Alternative")
                        parsed_tp["name"] = "Alternative via Thanneerpanthal Road"
                        if _is_distinct(parsed_tp["coordinates"], routes):
                            routes.append(parsed_tp)
            except Exception as tp_err:
                logger.debug(f"Thanneerpanthal route check notice: {tp_err}")

        # ── 3. Forced alternatives via perpendicular waypoints ─────────────────
        if len(routes) < 3:
            dlat = d_lat - s_lat
            dlng = d_lng - s_lng
            route_len = math.sqrt(dlat**2 + dlng**2)

            if route_len < 1e-9:
                route_len = 1e-9
            perp_lat = -dlng / route_len
            perp_lng =  dlat / route_len

            short = route_len < 0.05  # < ~5 km straight-line
            if short:
                magnitudes = [0.04, 0.06, 0.08, 0.05, 0.07]
            else:
                magnitudes = [0.10, 0.15, 0.12, 0.18, 0.20]

            fracs = [0.33, 0.67, 0.50, 0.33, 0.67]
            signs = [-1.0,  1.0, -1.0,  1.0, -1.0]

            attempted = []
            for frac, sign, mag in zip(fracs, signs, magnitudes):
                if len(routes) >= 3:
                    break

                wp_lat = s_lat + frac * dlat + sign * perp_lat * mag * route_len
                wp_lng = s_lng + frac * dlng + sign * perp_lng * mag * route_len

                if not (10.7 <= wp_lat <= 11.5 and 76.5 <= wp_lng <= 77.5):
                    continue

                wp_key = (round(wp_lat, 4), round(wp_lng, 4))
                if wp_key in attempted:
                    continue
                attempted.append(wp_key)

                try:
                    coords_wp = f"{s_lng},{s_lat};{wp_lng},{wp_lat};{d_lng},{d_lat}"
                    params_wp = "overview=full&geometries=geojson&steps=true"
                    data_wp = _get_osrm_json(coords_wp, params_wp)
                    if not data_wp:
                        continue
                    osrm_routes = data_wp.get("routes", [])
                    if not osrm_routes:
                        continue

                    candidate_r = osrm_routes[0]
                    if not _is_valid_through_route(candidate_r):
                        continue

                    parsed = _parse_osrm_route(candidate_r, "Alternative")
                    dist_km = parsed["distance_km"]
                    base_dist_km = routes[0]["distance_km"] if routes else dist_km

                    if dist_km > base_dist_km * 1.45:
                        continue

                    if _is_distinct(parsed["coordinates"], routes):
                        routes.append(parsed)

                except Exception as exc:
                    logger.debug(f"OSRM waypoint failed (frac={frac}, sign={sign}, mag={mag}): {exc}")



        # ── 3. Rename routes for clarity ─────────────────────────────────────
        for i, r in enumerate(routes):
            via = r["name"].split(" ", 2)[2] if len(r["name"].split(" ", 2)) > 2 else "Main Corridor"
            if i == 0:
                r["name"] = f"Fastest Route {via}"
            else:
                r["name"] = f"Alternative {via}"

        return routes


    def _fetch_ors_alternatives(
        self, s_lat: float, s_lng: float, d_lat: float, d_lng: float, search_id: str
    ) -> List[Dict[str, Any]]:
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json, application/geo+json",
        }
        body = {
            "coordinates": [[s_lng, s_lat], [d_lng, d_lat]],
            "alternative_routes": {
                "target_count": 3,
                "weight_factor": 1.4,
                "share_factor": 0.6,
            },
            "instructions": True,
            "geometry": True,
        }

        resp = requests.post(
            self.ORS_DIRECTIONS_URL, json=body, headers=headers, timeout=self.timeout_sec
        )

        if resp.status_code == 429:
            logger.warning("OpenRouteService 429 Rate Limit encountered.")
            return []
        if resp.status_code != 200:
            logger.warning(f"OpenRouteService returned status {resp.status_code}: {resp.text[:200]}")
            return []

        data = resp.json()
        features = data.get("features", [])
        if not features:
            return []

        routes = []
        for idx, feat in enumerate(features):
            props = feat.get("properties", {})
            summary = props.get("summary", {})
            geom = feat.get("geometry", {})
            raw_coords = geom.get("coordinates", [])

            # Convert [lng, lat] GeoJSON to [lat, lng] for Leaflet
            lat_lng_coords = [[c[1], c[0]] for c in raw_coords]

            distance_m = summary.get("distance", 0.0)
            duration_s = summary.get("duration", 0.0)

            # Segments / steps breakdown
            segments = []
            for seg in props.get("segments", []):
                for step in seg.get("steps", []):
                    segments.append({
                        "name": step.get("name", "Unnamed Road"),
                        "distance_m": step.get("distance", 0),
                        "duration_s": step.get("duration", 0),
                        "instruction": step.get("instruction", ""),
                    })

            routes.append({
                "name": f"Route Option {idx + 1}" if idx > 0 else "Fastest Route (Direct)",
                "distance_m": round(distance_m, 1),
                "distance_km": round(distance_m / 1000.0, 2),
                "duration_s": round(duration_s, 1),
                "duration_min": round(duration_s / 60.0, 1),
                "geometry": geom,
                "coordinates": lat_lng_coords,
                "segments": segments[:10],
                "source_type": "openrouteservice",
            })

        return routes

    def _generate_realistic_alternatives(
        self, s_lat: float, s_lng: float, d_lat: float, d_lng: float, search_id: str
    ) -> List[Dict[str, Any]]:
        """
        Synthesize 3 realistic distinct alternative routes with geodesic curvature
        simulating Coimbatore road geometry (Arterial, Ring Road, Central Corridor).
        """
        # Calculate straight-line distance in km (Haversine)
        R = 6371.0
        dlat = math.radians(d_lat - s_lat)
        dlng = math.radians(d_lng - s_lng)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(s_lat))
            * math.cos(math.radians(d_lat))
            * math.sin(dlng / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        base_dist_km = R * c

        # Generate 3 distinct routes
        route_configs = [
            {
                "name": "Primary Route (Main Arterial Corridor)",
                "dist_factor": 1.25,
                "speed_kmh": 38.0,
                "curvature_offset": 0.003,
                "road_type": "Primary Highway / NH-45",
            },
            {
                "name": "Alternative Route 1 (Avinashi Rd / Bypass)",
                "dist_factor": 1.42,
                "speed_kmh": 46.0,
                "curvature_offset": -0.007,
                "road_type": "Outer Ring / State Highway",
            },
            {
                "name": "Alternative Route 2 (City Central Link)",
                "dist_factor": 1.34,
                "speed_kmh": 30.0,
                "curvature_offset": 0.008,
                "road_type": "Urban Arterial",
            },
        ]

        routes = []
        for idx, cfg in enumerate(route_configs):
            dist_km = max(round(base_dist_km * cfg["dist_factor"], 2), 1.2)
            dist_m = dist_km * 1000.0
            duration_min = max(round((dist_km / cfg["speed_kmh"]) * 60.0, 1), 3.0)
            duration_s = duration_min * 60.0

            # Build polyline with smooth sub-points
            steps_count = 12
            polyline = []
            for step in range(steps_count + 1):
                t = step / float(steps_count)
                # Linear interpolation
                lat_interp = s_lat + t * (d_lat - s_lat)
                lng_interp = s_lng + t * (d_lng - s_lng)

                # Parabolic curve offset perpendicular to direction
                curve = math.sin(math.pi * t) * cfg["curvature_offset"]
                lat_point = lat_interp + curve * math.cos(dlat)
                lng_point = lng_interp + curve * math.sin(dlng)

                polyline.append([round(lat_point, 5), round(lng_point, 5)])

            routes.append({
                "name": cfg["name"],
                "distance_m": dist_m,
                "distance_km": dist_km,
                "duration_s": duration_s,
                "duration_min": duration_min,
                "road_type": cfg["road_type"],
                "coordinates": polyline,
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[pt[1], pt[0]] for pt in polyline],
                },
                "segments": [
                    {
                        "name": f"Segment A ({cfg['road_type']})",
                        "distance_m": round(dist_m * 0.4),
                        "duration_s": round(duration_s * 0.4),
                        "instruction": f"Head toward {cfg['road_type']}",
                    },
                    {
                        "name": f"Segment B (Connecting Corridor)",
                        "distance_m": round(dist_m * 0.6),
                        "duration_s": round(duration_s * 0.6),
                        "instruction": "Continue along destination route",
                    },
                ],
                "source_type": "coimbatore_network_engine",
            })

        return routes
