"""
backend/services/event_service.py — Public Events, Festivals, Marriages & Bottleneck Impact Service.

Impact Formula Documentation:
=============================
Event Impact Score (0.0 to 1.0) on a given road route geometry is computed via:
  Impact Score = min(1.0, BaseLevel * CrowdWeight * ProximityFactor * TimeOverlap)

Where:
1. BaseLevel (from impact_level):
   - CRITICAL : 1.00 (Major state festival, VIP political rally, road closures)
   - HIGH     : 0.75 (Grand temple festival procession, major convention, 5k+ wedding)
   - MEDIUM   : 0.50 (Standard marriage hall gathering, college symposium)
   - LOW      : 0.25 (Small community/school event)

2. CrowdWeight (from expected_crowd):
   - crowd >= 10,000       : 1.30
   - 5,000 <= crowd < 10,000 : 1.15
   - 1,000 <= crowd < 5,000  : 1.00
   - crowd < 1,000          : 0.80

3. ProximityFactor (perpendicular distance d from closest route point to event venue):
   - d < 500 m             : 1.00 (Direct choke point on route)
   - 500 m <= d < 1500 m   : 0.75 (High spillover onto connecting arterials)
   - 1500 m <= d < 3000 m  : 0.45 (Moderate secondary delay)
   - 3000 m <= d < 5000 m  : 0.15 (Minor peripheral delay)
   - d >= 5000 m           : 0.00 (No route impact)

4. TimeOverlap:
   - 1.00 : Target travel datetime falls strictly inside [start_time, end_time]
   - 0.50 : Target travel datetime is within +/- 1 hour of event start/end (dispersal/arrival surge)
   - 0.00 : Outside active event window
"""
from __future__ import annotations

import math
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
from bson import ObjectId
from loguru import logger

from backend.models.events import EventModel, VALID_EVENT_TYPES, VALID_IMPACT_LEVELS
from backend.repositories.event_repository import EventRepository


def _haversine_distance_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance in meters between two lat/lng points."""
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class EventService:
    def __init__(self, event_repo: Optional[EventRepository] = None):
        self.event_repo = event_repo or EventRepository()

    def get_active_events(
        self,
        lat: float,
        lng: float,
        radius_km: float = 10.0,
        target_datetime: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return active events within radius_km of the provided coordinate.
        """
        check_time = target_datetime or datetime.now(timezone.utc)
        all_active = self.event_repo.get_active_events(check_time)

        filtered = []
        max_dist_m = radius_km * 1000.0
        for ev in all_active:
            ev_lat = float(ev.get("lat") or ev.get("location", {}).get("coordinates", [0, 0])[1])
            ev_lng = float(ev.get("lng") or ev.get("location", {}).get("coordinates", [0, 0])[0])
            dist_m = _haversine_distance_m(lat, lng, ev_lat, ev_lng)
            if dist_m <= max_dist_m:
                ev_copy = dict(ev)
                ev_copy["distance_to_center_km"] = round(dist_m / 1000.0, 2)
                filtered.append(ev_copy)

        return filtered

    def calculate_event_impact(
        self,
        event: Dict[str, Any],
        route_geometry: List[List[float]] | Dict[str, Any],
        target_datetime: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Calculate impact score (0.0 to 1.0) and bottleneck delay factor of an event on a route.
        """
        check_time = target_datetime or datetime.now(timezone.utc)

        # Extract event coordinates
        ev_lat = float(event.get("lat") or event.get("location", {}).get("coordinates", [0, 0])[1])
        ev_lng = float(event.get("lng") or event.get("location", {}).get("coordinates", [0, 0])[0])

        # 1. Base Level
        imp_level = str(event.get("impact_level", "MEDIUM")).upper()
        base_weights = {
            "CRITICAL": 1.00,
            "HIGH": 0.75,
            "MEDIUM": 0.50,
            "LOW": 0.25,
        }
        base_weight = base_weights.get(imp_level, 0.50)

        # 2. Crowd Weight
        crowd = int(event.get("expected_crowd", 500))
        if crowd >= 10000:
            crowd_weight = 1.30
        elif crowd >= 5000:
            crowd_weight = 1.15
        elif crowd >= 1000:
            crowd_weight = 1.00
        else:
            crowd_weight = 0.80

        # 3. Proximity Factor: Find minimum distance from route points to event venue
        coords_list: List[List[float]] = []
        if isinstance(route_geometry, list):
            coords_list = route_geometry
        elif isinstance(route_geometry, dict):
            coords_list = route_geometry.get("coordinates", [])

        min_dist_m = float("inf")
        for pt in coords_list:
            if len(pt) >= 2:
                # Leaflet: [lat, lng], GeoJSON: [lng, lat]
                pt_lat, pt_lng = pt[0], pt[1]
                d = _haversine_distance_m(pt_lat, pt_lng, ev_lat, ev_lng)
                if d < min_dist_m:
                    min_dist_m = d

        if min_dist_m == float("inf"):
            min_dist_m = 5000.0

        if min_dist_m < 500.0:
            prox_factor = 1.00
        elif min_dist_m < 1500.0:
            prox_factor = 0.75
        elif min_dist_m < 3000.0:
            prox_factor = 0.45
        elif min_dist_m < 5000.0:
            prox_factor = 0.15
        else:
            prox_factor = 0.00

        # 4. Time Overlap
        st = event.get("start_time")
        et = event.get("end_time")

        if isinstance(st, str):
            try:
                st = datetime.fromisoformat(st.replace("Z", "+00:00"))
            except Exception:
                st = None
        if isinstance(et, str):
            try:
                et = datetime.fromisoformat(et.replace("Z", "+00:00"))
            except Exception:
                et = None

        time_overlap = 0.0
        if st is not None:
            # Handle timezone awareness
            if st.tzinfo is None:
                st = st.replace(tzinfo=timezone.utc)
            if et and et.tzinfo is None:
                et = et.replace(tzinfo=timezone.utc)
            if check_time.tzinfo is None:
                check_time = check_time.replace(tzinfo=timezone.utc)

            event_end = et or (st + timedelta(hours=6))

            if st <= check_time <= event_end:
                time_overlap = 1.00
            elif (st - timedelta(hours=1)) <= check_time <= (event_end + timedelta(hours=1)):
                time_overlap = 0.50
            else:
                time_overlap = 0.00
        else:
            time_overlap = 1.00

        # Raw Score
        raw_score = base_weight * crowd_weight * prox_factor * time_overlap
        final_score = min(max(round(raw_score, 2), 0.0), 1.0)

        delay_multiplier = round(1.0 + (final_score * 0.5), 2)  # up to 1.5x delay

        return {
            "event_id": str(event.get("_id", "")),
            "title": event.get("title", "Unnamed Event"),
            "event_type": event.get("event_type", "OTHER"),
            "impact_level": imp_level,
            "impact_score": final_score,
            "delay_multiplier": delay_multiplier,
            "min_distance_m": round(min_dist_m, 1),
            "time_overlap_factor": time_overlap,
            "is_impacting": final_score > 0.15,
        }

    def evaluate_route_events(
        self,
        route_coordinates: List[List[float]],
        target_datetime: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate all active events against a route polyline and return total impact.
        """
        check_time = target_datetime or datetime.now(timezone.utc)
        all_events = self.event_repo.get_active_events(check_time)

        impacting_events = []
        max_impact = 0.0

        for ev in all_events:
            res = self.calculate_event_impact(ev, route_coordinates, check_time)
            if res["is_impacting"]:
                impacting_events.append(res)
                if res["impact_score"] > max_impact:
                    max_impact = res["impact_score"]

        # Composite impact score capped at 1.0
        composite_score = min(round(sum(e["impact_score"] for e in impacting_events), 2), 1.0)

        return {
            "total_impact_score": composite_score,
            "max_single_impact": max_impact,
            "impacting_events_count": len(impacting_events),
            "events": impacting_events,
        }

    # -------------------------------------------------------------------------
    # CRUD Operations
    # -------------------------------------------------------------------------

    def create_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and create a new event document."""
        title = data.get("title", "").strip()
        if not title:
            raise ValueError("Event title is required.")

        event_type = str(data.get("event_type", "OTHER")).upper()
        if event_type not in VALID_EVENT_TYPES:
            raise ValueError(f"Invalid event_type '{event_type}'. Valid types: {list(VALID_EVENT_TYPES)}")

        # Location formatting
        lat = float(data.get("lat", 11.0168))
        lng = float(data.get("lng", 76.9558))

        doc = {
            "title": title,
            "event_type": event_type,
            "description": data.get("description", ""),
            "venue_name": data.get("venue_name", "Coimbatore Venue"),
            "road_name": data.get("road_name", "Arterial Road"),
            "lat": lat,
            "lng": lng,
            "location": {"type": "Point", "coordinates": [lng, lat]},
            "radius_m": float(data.get("radius_m", 1500.0)),
            "expected_crowd": int(data.get("expected_crowd", 500)),
            "impact_level": str(data.get("impact_level", "MEDIUM")).upper(),
            "start_time": data.get("start_time") or datetime.now(timezone.utc),
            "end_time": data.get("end_time"),
            "status": "ACTIVE",
            "is_active": True,
            "tamil_title": data.get("tamil_title"),
            "tamil_month": data.get("tamil_month"),
            "affected_corridors": data.get("affected_corridors", []),
            "nakshatram": data.get("nakshatram"),
            "tithi": data.get("tithi"),
            "muhurtham_time": data.get("muhurtham_time"),
            "is_tamil_calendar": bool(data.get("is_tamil_calendar", False)),
        }

        # Parse date strings if passed
        if isinstance(doc["start_time"], str):
            doc["start_time"] = datetime.fromisoformat(doc["start_time"].replace("Z", "+00:00"))
        if isinstance(doc.get("end_time"), str):
            doc["end_time"] = datetime.fromisoformat(doc["end_time"].replace("Z", "+00:00"))

        inserted_id = self.event_repo.create(doc)
        doc["_id"] = inserted_id
        return doc

    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing event by ID."""
        if isinstance(updates.get("start_time"), str):
            updates["start_time"] = datetime.fromisoformat(updates["start_time"].replace("Z", "+00:00"))
        if isinstance(updates.get("end_time"), str):
            updates["end_time"] = datetime.fromisoformat(updates["end_time"].replace("Z", "+00:00"))

        # Keep lat/lng synced with GeoJSON if passed
        if "lat" in updates or "lng" in updates:
            lat = float(updates.get("lat", 11.0168))
            lng = float(updates.get("lng", 76.9558))
            updates["location"] = {"type": "Point", "coordinates": [lng, lat]}

        success = self.event_repo.update(event_id, updates)
        if success:
            return self.event_repo.get_by_id(event_id)
        return None

    def delete_event(self, event_id: str) -> bool:
        """Delete an event by ID."""
        return self.event_repo.delete(event_id)

    def list_events(
        self,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        date_str: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List and filter events."""
        return self.event_repo.filter_events(event_type, status, date_str)
