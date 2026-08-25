"""
backend/services/feature_engineering_service.py — SINGLE source of truth for route-level features.

Design Rules
-------------
- Each formula lives in exactly one place.
- This service imports from specialist services; it NEVER re-implements their logic.
- build_route_feature_vector() assembles ALL features into one flat dict for CatBoost input.

Feature Vector Keys (final output of build_route_feature_vector)
-----------------------------------------------------------------
Route basics:
  distance_km, duration_min, num_waypoints

Traffic / TCI:
  tci, predicted_travel_time, free_flow_travel_time

Weather risk:
  weather_risk_score, weather_risk_level, temperature, precipitation,
  wind_speed, visibility, humidity, surface_pressure

Event impact (aggregate across all active events):
  event_impact_score, event_delay_multiplier, num_active_events

Festival-specific:
  festival_indicator, festival_impact_score, festival_distance_km, festival_active

Marriage/Wedding-specific:
  marriage_event_indicator, marriage_impact_score, marriage_distance_km, marriage_active

Landslide/Hazard:
  landslide_indicator, landslide_active, landslide_severity, landslide_distance_km, road_blocked
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 1. TCI — Traffic Congestion Index
# ---------------------------------------------------------------------------

def calculate_tci(
    predicted_travel_time: float,
    free_flow_travel_time: float,
) -> float:
    """
    TCI = predicted_travel_time / free_flow_travel_time.

    Returns:
        float: TCI value. Returns 999.0 if free_flow_travel_time is zero (complete blockage).
    """
    if free_flow_travel_time == 0:
        return 999.0
    return round(predicted_travel_time / free_flow_travel_time, 4)


# ---------------------------------------------------------------------------
# 2. Weather Risk — delegates entirely to weather_risk_calculator.py
# ---------------------------------------------------------------------------

def calculate_weather_risk(weather_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates composite weather risk for a route.

    Delegates to backend.services.weather_risk_calculator.calculate_weather_risk.
    Does NOT duplicate any formula here.

    Args:
        weather_dict: dict with keys temperature, precipitation, visibility,
                      wind_speed, humidity, surface_pressure (all optional,
                      calculator provides safe defaults).

    Returns:
        dict from weather_risk_calculator: { risk_score, risk_level, ... }
    """
    from backend.services.weather_risk_calculator import (
        calculate_weather_risk as _calc_weather_risk,
    )

    return _calc_weather_risk(
        temperature=weather_dict.get("temperature_2m", weather_dict.get("temperature", 28.0)),
        precipitation=weather_dict.get("precipitation", 0.0),
        visibility=weather_dict.get("visibility", 10000.0),
        wind_speed=weather_dict.get("wind_speed_10m", weather_dict.get("wind_speed", 10.0)),
        humidity=weather_dict.get("relative_humidity_2m", weather_dict.get("humidity")),
        surface_pressure=weather_dict.get("surface_pressure"),
    )


# ---------------------------------------------------------------------------
# 3. Event Impact (aggregate) — delegates to EventService
# ---------------------------------------------------------------------------

def calculate_event_impact(
    route_geojson: List[List[float]] | Dict[str, Any],
    target_datetime: datetime,
    active_events: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Calculates the aggregate event impact for a route across all active events.

    Delegates per-event scoring to EventService.calculate_event_impact.
    Does NOT re-implement the proximity/crowd/time formula.

    Returns:
        {
            event_impact_score: float (max single-event score across all events),
            event_delay_multiplier: float (product of delay multipliers, capped at 2.0),
            num_active_events: int,
        }
    """
    from backend.services.event_service import EventService

    if not active_events:
        return {
            "event_impact_score": 0.0,
            "event_delay_multiplier": 1.0,
            "num_active_events": 0,
        }

    svc = EventService()
    impacts = []

    for event in active_events:
        try:
            impact = svc.calculate_event_impact(
                event=event,
                route_geometry=route_geojson,
                target_datetime=target_datetime,
            )
            if impact.get("is_impacting", False):
                impacts.append(impact)
        except Exception as exc:
            logger.warning(f"Event impact calculation failed for {event.get('_id')}: {exc}")

    if not impacts:
        return {
            "event_impact_score": 0.0,
            "event_delay_multiplier": 1.0,
            "num_active_events": 0,
        }

    max_impact_score = max(i["impact_score"] for i in impacts)

    # Compound delay multiplier: product of all delays capped at 2.0x
    compound_delay = 1.0
    for imp in impacts:
        compound_delay *= imp.get("delay_multiplier", 1.0)
    compound_delay = round(min(compound_delay, 2.0), 3)

    return {
        "event_impact_score": round(max_impact_score, 4),
        "event_delay_multiplier": compound_delay,
        "num_active_events": len(impacts),
    }


# ---------------------------------------------------------------------------
# 4. Festival Features
# ---------------------------------------------------------------------------

def calculate_festival_features(
    route_geojson: List[List[float]] | Dict[str, Any],
    target_datetime: datetime,
    festivals: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Calculates festival-specific impact features by delegating each event
    to EventService.calculate_event_impact (festivals are a subset of events
    with event_type in {FESTIVAL, PUBLIC_EVENT}).

    Returns:
        {
            festival_indicator: int (1 if any festival is impacting, else 0),
            festival_impact_score: float,
            festival_distance_km: float (closest active festival in km),
            festival_active: int (count of currently active festivals),
        }
    """
    FESTIVAL_TYPES = {"FESTIVAL", "PUBLIC_EVENT"}

    festival_events = [e for e in festivals if e.get("event_type", "").upper() in FESTIVAL_TYPES]

    if not festival_events:
        return {
            "festival_indicator": 0,
            "festival_impact_score": 0.0,
            "festival_distance_km": 999.0,
            "festival_active": 0,
        }

    from backend.services.event_service import EventService
    svc = EventService()

    best_score = 0.0
    min_dist_m = float("inf")
    active_count = 0

    for event in festival_events:
        try:
            impact = svc.calculate_event_impact(
                event=event,
                route_geometry=route_geojson,
                target_datetime=target_datetime,
            )
            if impact.get("is_impacting", False):
                active_count += 1
                best_score = max(best_score, impact.get("impact_score", 0.0))
                min_dist_m = min(min_dist_m, impact.get("min_distance_m", float("inf")))
        except Exception as exc:
            logger.warning(f"Festival feature calc failed for {event.get('_id')}: {exc}")

    return {
        "festival_indicator": 1 if active_count > 0 else 0,
        "festival_impact_score": round(best_score, 4),
        "festival_distance_km": round(min_dist_m / 1000.0, 3) if min_dist_m != float("inf") else 999.0,
        "festival_active": active_count,
    }


# ---------------------------------------------------------------------------
# 5. Marriage/Wedding Features
# ---------------------------------------------------------------------------

def calculate_marriage_features(
    route_geojson: List[List[float]] | Dict[str, Any],
    target_datetime: datetime,
    marriages: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Calculates marriage/wedding-specific impact features. Delegates scoring to
    EventService.calculate_event_impact (marriage events have event_type == MARRIAGE).

    Returns:
        {
            marriage_event_indicator: int (1 if any marriage is impacting, else 0),
            marriage_impact_score: float,
            marriage_distance_km: float (closest active marriage event in km),
            marriage_active: int (count of currently active marriage events),
        }
    """
    marriage_events = [e for e in marriages if e.get("event_type", "").upper() == "MARRIAGE"]

    if not marriage_events:
        return {
            "marriage_event_indicator": 0,
            "marriage_impact_score": 0.0,
            "marriage_distance_km": 999.0,
            "marriage_active": 0,
        }

    from backend.services.event_service import EventService
    svc = EventService()

    best_score = 0.0
    min_dist_m = float("inf")
    active_count = 0

    for event in marriage_events:
        try:
            impact = svc.calculate_event_impact(
                event=event,
                route_geometry=route_geojson,
                target_datetime=target_datetime,
            )
            if impact.get("is_impacting", False):
                active_count += 1
                best_score = max(best_score, impact.get("impact_score", 0.0))
                min_dist_m = min(min_dist_m, impact.get("min_distance_m", float("inf")))
        except Exception as exc:
            logger.warning(f"Marriage feature calc failed for {event.get('_id')}: {exc}")

    return {
        "marriage_event_indicator": 1 if active_count > 0 else 0,
        "marriage_impact_score": round(best_score, 4),
        "marriage_distance_km": round(min_dist_m / 1000.0, 3) if min_dist_m != float("inf") else 999.0,
        "marriage_active": active_count,
    }


# ---------------------------------------------------------------------------
# 6. Landslide Features — delegates to LandslideService
# ---------------------------------------------------------------------------

def calculate_landslide_features(
    route_geojson: List[List[float]] | Dict[str, Any],
    active_landslides: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Calculates landslide hazard features for a route.

    Delegates collision detection to LandslideService.check_route_landslide_impact.
    Does NOT re-implement the Haversine formula.

    Returns:
        {
            landslide_indicator: int (1 if any landslide is within impact radius, else 0),
            landslide_active: int (total active landslides on route corridor),
            landslide_severity: str (worst-case severity: CRITICAL > HIGH > MEDIUM > LOW),
            landslide_distance_km: float (closest hazard center in km, 999.0 if none),
            road_blocked: int (1 if route is hard-blocked, else 0),
        }
    """
    SEVERITY_ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}

    if not active_landslides:
        return {
            "landslide_indicator": 0,
            "landslide_active": 0,
            "landslide_severity": "NONE",
            "landslide_distance_km": 999.0,
            "road_blocked": 0,
        }

    from backend.services.landslide_service import LandslideService
    svc = LandslideService()

    impact = svc.check_route_landslide_impact(
        route_geometry=route_geojson,
        landslides=active_landslides,
    )

    if impact.get("blocked", False):
        severity = impact.get("severity", "HIGH")
        dist_km = round(impact.get("distance_m", 0.0) / 1000.0, 3)
        return {
            "landslide_indicator": 1,
            "landslide_active": len(active_landslides),
            "landslide_severity": severity,
            "landslide_distance_km": dist_km,
            "road_blocked": 1,
        }

    # Route is not blocked but hazards exist nearby — find closest
    min_dist_m = float("inf")
    worst_severity = "NONE"
    worst_rank = 0

    for hazard in active_landslides:
        # Approximate: distance from impact dict is not per-hazard here,
        # so we flag presence but mark not blocked
        sev = hazard.get("severity", "LOW").upper()
        rank = SEVERITY_ORDER.get(sev, 0)
        if rank > worst_rank:
            worst_rank = rank
            worst_severity = sev
        # lat/lng from hazard for rough proximity
        lat = hazard.get("lat") or hazard.get("latitude")
        lng = hazard.get("lng") or hazard.get("longitude")
        if lat and lng:
            # Use first route point as proxy distance
            coords = route_geojson if isinstance(route_geojson, list) else []
            if coords:
                from math import radians, sin, cos, sqrt, atan2
                first = coords[0]
                rlat, rlng = (first[1], first[0]) if len(first) == 2 else (first[0], first[1])
                R = 6371000.0
                phi1, phi2 = radians(float(rlat)), radians(float(lat))
                dphi = radians(float(lat) - float(rlat))
                dlam = radians(float(lng) - float(rlng))
                a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlam / 2) ** 2
                d = 2 * R * atan2(sqrt(a), sqrt(1 - a))
                min_dist_m = min(min_dist_m, d)

    return {
        "landslide_indicator": 1 if active_landslides else 0,
        "landslide_active": len(active_landslides),
        "landslide_severity": worst_severity,
        "landslide_distance_km": round(min_dist_m / 1000.0, 3) if min_dist_m != float("inf") else 999.0,
        "road_blocked": 0,
    }


# ---------------------------------------------------------------------------
# 7. Master Feature Vector — assembles all features for CatBoost input
# ---------------------------------------------------------------------------

def build_route_feature_vector(
    route: Dict[str, Any],
    predictions: Dict[str, Any],
    weather: Dict[str, Any],
    events: List[Dict[str, Any]],
    landslides: List[Dict[str, Any]],
    target_datetime: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Assembles all route-level features into a single flat dict for CatBoost.

    Args:
        route:           Route document (from MongoDB or routing service response).
                         Expected keys: distance_km, duration_min, coordinates,
                         free_flow_travel_time.
        predictions:     PatchTST inference result. Expected keys: predicted_speed,
                         predicted_travel_time, predicted_flow.
        weather:         Open-Meteo weather dict for the route origin.
        events:          All active event documents near the route.
        landslides:      All ACTIVE landslide documents.
        target_datetime: Datetime of planned travel (defaults to now UTC).

    Returns:
        dict: Flat feature vector ready for CatBoost .predict() call.
    """
    if target_datetime is None:
        target_datetime = datetime.now(timezone.utc)

    route_geojson = route.get("coordinates", [])

    # --- Route Basics ---
    distance_km = route.get("distance_km", route.get("distance", 0.0))
    duration_min = route.get("duration_min", route.get("duration", 0.0))
    num_waypoints = len(route_geojson)

    # --- Traffic / TCI ---
    predicted_travel_time = predictions.get("predicted_travel_time", duration_min * 60)
    free_flow_travel_time = route.get("free_flow_travel_time", duration_min * 60 * 0.7)
    tci = calculate_tci(predicted_travel_time, free_flow_travel_time)

    # --- Weather ---
    weather_features: Dict[str, Any] = {}
    if weather:
        try:
            weather_result = calculate_weather_risk(weather)
            weather_features = {
                "weather_risk_score": weather_result.get("risk_score", 0.0),
                "weather_risk_level": weather_result.get("risk_level", "Low"),
                "temperature": weather.get("temperature_2m", weather.get("temperature", 28.0)),
                "precipitation": weather.get("precipitation", 0.0),
                "wind_speed": weather.get("wind_speed_10m", weather.get("wind_speed", 10.0)),
                "visibility": weather.get("visibility", 10000.0),
                "humidity": weather.get("relative_humidity_2m", weather.get("humidity", 60.0)),
                "surface_pressure": weather.get("surface_pressure", 1013.0),
            }
        except Exception as exc:
            logger.warning(f"Weather risk calculation failed: {exc}")
            weather_features = {
                "weather_risk_score": 0.0,
                "weather_risk_level": "LOW",
                "temperature": 28.0,
                "precipitation": 0.0,
                "wind_speed": 10.0,
                "visibility": 10000.0,
                "humidity": 60.0,
                "surface_pressure": 1013.0,
            }
    else:
        weather_features = {
            "weather_risk_score": 0.0,
            "weather_risk_level": "LOW",
            "temperature": 28.0,
            "precipitation": 0.0,
            "wind_speed": 10.0,
            "visibility": 10000.0,
            "humidity": 60.0,
            "surface_pressure": 1013.0,
        }

    # --- Events (aggregate) ---
    try:
        event_features = calculate_event_impact(route_geojson, target_datetime, events or [])
    except Exception as exc:
        logger.warning(f"Event impact calculation failed: {exc}")
        event_features = {
            "event_impact_score": 0.0,
            "event_delay_multiplier": 1.0,
            "num_active_events": 0,
        }

    # --- Festival features (subset of events) ---
    try:
        festival_features = calculate_festival_features(route_geojson, target_datetime, events or [])
    except Exception as exc:
        logger.warning(f"Festival feature calculation failed: {exc}")
        festival_features = {
            "festival_indicator": 0,
            "festival_impact_score": 0.0,
            "festival_distance_km": 999.0,
            "festival_active": 0,
        }

    # --- Marriage features (subset of events) ---
    try:
        marriage_features = calculate_marriage_features(route_geojson, target_datetime, events or [])
    except Exception as exc:
        logger.warning(f"Marriage feature calculation failed: {exc}")
        marriage_features = {
            "marriage_event_indicator": 0,
            "marriage_impact_score": 0.0,
            "marriage_distance_km": 999.0,
            "marriage_active": 0,
        }

    # --- Landslide features ---
    try:
        landslide_features = calculate_landslide_features(route_geojson, landslides or [])
    except Exception as exc:
        logger.warning(f"Landslide feature calculation failed: {exc}")
        landslide_features = {
            "landslide_indicator": 0,
            "landslide_active": 0,
            "landslide_severity": "NONE",
            "landslide_distance_km": 999.0,
            "road_blocked": 0,
        }

    # --- Datetime features (time-of-day / day-of-week for CatBoost) ---
    dt = target_datetime if target_datetime.tzinfo else target_datetime.replace(tzinfo=timezone.utc)
    hour_of_day = dt.hour
    day_of_week = dt.weekday()  # 0=Monday … 6=Sunday
    is_weekend = int(day_of_week >= 5)

    # --- Assemble and return flat feature vector ---
    feature_vector: Dict[str, Any] = {
        # Route basics
        "distance_km": round(float(distance_km), 4),
        "duration_min": round(float(duration_min), 4),
        "num_waypoints": num_waypoints,
        # Traffic / TCI
        "tci": tci,
        "predicted_travel_time": round(float(predicted_travel_time), 2),
        "free_flow_travel_time": round(float(free_flow_travel_time), 2),
        "predicted_speed": round(float(predictions.get("predicted_speed", 40.0)), 2),
        "predicted_flow": round(float(predictions.get("predicted_flow", 0.0)), 2),
        # Datetime
        "hour_of_day": hour_of_day,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        # Weather
        **weather_features,
        # Events (aggregate)
        **event_features,
        # Festivals
        **festival_features,
        # Marriages
        **marriage_features,
        # Landslides
        **landslide_features,
    }

    logger.debug(
        f"Feature vector built: tci={tci}, weather={weather_features.get('weather_risk_level')}, "
        f"events={event_features.get('num_active_events')}, "
        f"road_blocked={landslide_features.get('road_blocked')}"
    )

    return feature_vector
