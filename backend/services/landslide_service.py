"""
backend/services/landslide_service.py — Landslide Hazard Management & Road Blockage Engine.

CRITICAL ARCHITECTURAL RULES:
  1. PatchTST does NOT detect landslides. Landslides are strictly Admin-entered.
  2. A BLOCKED route MUST NOT be recommended under any circumstances.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId
from loguru import logger

from backend.database import get_db
from backend.models.landslides import LandslideModel
from backend.repositories.landslide_repository import LandslideRepository
from backend.repositories.notification_repository import NotificationRepository
from backend.repositories.system_log_repository import SystemLogRepository


def _haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance in meters between two coordinates."""
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class LandslideService:
    def __init__(
        self,
        landslide_repo: Optional[LandslideRepository] = None,
        notif_repo: Optional[NotificationRepository] = None,
        sys_repo: Optional[SystemLogRepository] = None,
    ):
        self.landslide_repo = landslide_repo or LandslideRepository()
        self.notif_repo = notif_repo or NotificationRepository()
        self.sys_repo = sys_repo or SystemLogRepository()

    def get_active_landslides(self) -> List[Dict[str, Any]]:
        """Return all currently ACTIVE landslide hazards."""
        return self.landslide_repo.get_active_landslides()

    def check_route_landslide_impact(
        self,
        route_geometry: List[List[float]] | Dict[str, Any],
        landslides: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Check if any coordinate along the route polyline falls within the hazard radius of an active landslide.
        Returns: { "blocked": bool, "landslide_id": str, "distance_m": float, "severity": str, ... }
        """
        active_hazards = landslides if landslides is not None else self.get_active_landslides()
        if not active_hazards:
            return {"blocked": False}

        # Extract route points [lat, lng]
        coords: List[List[float]] = []
        if isinstance(route_geometry, list):
            coords = route_geometry
        elif isinstance(route_geometry, dict):
            coords = route_geometry.get("coordinates", [])

        if not coords:
            return {"blocked": False}

        for hazard in active_hazards:
            h_lat = float(hazard.get("lat") or hazard.get("location", {}).get("coordinates", [0, 0])[1])
            h_lng = float(hazard.get("lng") or hazard.get("location", {}).get("coordinates", [0, 0])[0])
            radius_m = float(hazard.get("radius_m", 2500.0))

            min_dist = float("inf")
            for pt in coords:
                if len(pt) >= 2:
                    dist = _haversine_m(pt[0], pt[1], h_lat, h_lng)
                    if dist < min_dist:
                        min_dist = dist

            # Blockage Collision Detected
            if min_dist <= radius_m:
                logger.warning(
                    f"Route collision with Landslide '{hazard.get('title')}' (Dist: {min_dist:.1f}m <= Radius: {radius_m}m). BLOCKING ROUTE."
                )
                return {
                    "blocked": True,
                    "landslide_id": str(hazard.get("_id", "")),
                    "title": hazard.get("title", "Active Landslide Blockage"),
                    "severity": hazard.get("severity", "HIGH"),
                    "risk_level": hazard.get("risk_level", "High"),
                    "region_name": hazard.get("region_name", "Western Ghats Corridor"),
                    "road_name": hazard.get("road_name", "Ghat Highway"),
                    "distance_m": round(min_dist, 1),
                    "radius_m": radius_m,
                    "reported_at": hazard.get("reported_at"),
                }

        return {"blocked": False}

    def evaluate_routes_for_landslides(
        self, routes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate a list of candidate routes against active landslides.
        ENFORCES CRITICAL RULE: A blocked route is NEVER recommended.
        """
        active_hazards = self.get_active_landslides()
        if not routes:
            return []

        recommended_assigned = False

        for idx, route in enumerate(routes):
            coords = route.get("coordinates", [])
            impact = self.check_route_landslide_impact(coords, active_hazards)

            if impact.get("blocked", False):
                route["is_blocked"] = True
                route["is_recommended"] = False
                route["landslide_hazard"] = impact
                route["blockage_reason"] = (
                    f"Hazard Blockade: Landslide at {impact.get('region_name')} ({impact.get('road_name')})"
                )
            else:
                route["is_blocked"] = False
                route["landslide_hazard"] = None
                # First non-blocked route receives recommendation
                if not recommended_assigned:
                    route["is_recommended"] = True
                    recommended_assigned = True
                else:
                    route["is_recommended"] = False

        # If all routes are blocked, ensure none are marked recommended
        if not recommended_assigned and routes:
            logger.warning("ALL candidate routes are blocked by active landslides.")
            for r in routes:
                r["is_recommended"] = False

        return routes

    def activate_landslide(self, landslide_id: str) -> Optional[Dict[str, Any]]:
        """
        Activate a landslide alert, create notifications, and log audit event.
        """
        now = datetime.now(timezone.utc)
        updates = {
            "status": "ACTIVE",
            "is_active": True,
            "updated_at": now,
        }
        success = self.landslide_repo.update(landslide_id, updates)
        if not success:
            return None

        hazard = self.landslide_repo.get_by_id(landslide_id)
        if hazard:
            # Create Broadcast Notification using NotificationService
            try:
                from backend.services.notification_service import NotificationService
                notif_svc = NotificationService(self.db)
                notif_svc.create_notification(
                    user_id="broadcast_all",
                    type="LANDSLIDE_ALERT",
                    title=f"🚨 EMERGENCY: Landslide Activated at {hazard.get('region_name', 'Ghat Section')}",
                    message=f"Road segment {hazard.get('road_name', 'Highway')} is currently BLOCKED due to active landslide debris. RouteIQ has rerouted traffic.",
                    severity=hazard.get("severity", "CRITICAL"),
                    related_event_id=landslide_id
                )
            except Exception as notif_err:
                logger.warning(f"Failed to create broadcast notification: {notif_err}")

            # System Audit Log
            try:
                self.sys_repo.log(
                    level="WARNING",
                    source="landslide_service",
                    message=f"Landslide hazard '{hazard.get('title')}' activated.",
                    details={"landslide_id": landslide_id, "region": hazard.get("region_name")},
                )
            except Exception:
                pass

        return hazard

    def resolve_landslide(self, landslide_id: str) -> Optional[Dict[str, Any]]:
        """
        Resolve a landslide alert and remove road blockade.
        """
        now = datetime.now(timezone.utc)
        updates = {
            "status": "RESOLVED",
            "is_active": False,
            "resolved_at": now,
            "updated_at": now,
        }
        success = self.landslide_repo.update(landslide_id, updates)
        if not success:
            return None

        hazard = self.landslide_repo.get_by_id(landslide_id)
        if hazard:
            try:
                self.sys_repo.log(
                    level="INFO",
                    source="landslide_service",
                    message=f"Landslide hazard '{hazard.get('title')}' resolved. Road restriction lifted.",
                    details={"landslide_id": landslide_id},
                )
            except Exception:
                pass

        return hazard

    # -------------------------------------------------------------------------
    # CRUD Operations
    # -------------------------------------------------------------------------

    def create_landslide(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new landslide document."""
        title = data.get("title", "").strip()
        if not title:
            raise ValueError("Landslide title is required.")

        lat = float(data.get("lat", 11.2500))
        lng = float(data.get("lng", 76.9000))

        doc = {
            "title": title,
            "status": data.get("status", "ACTIVE").upper(),
            "is_active": data.get("status", "ACTIVE").upper() == "ACTIVE",
            "risk_level": data.get("risk_level", "High"),
            "severity": data.get("severity", "HIGH").upper(),
            "region_name": data.get("region_name", "Western Ghats Corridor"),
            "road_name": data.get("road_name", "Ghat Highway"),
            "lat": lat,
            "lng": lng,
            "location": {"type": "Point", "coordinates": [lng, lat]},
            "radius_m": float(data.get("radius_m", 2500.0)),
            "rainfall_mm": float(data.get("rainfall_mm", 45.0)),
            "description": data.get("description", "Debris and rockfall reported."),
            "reported_at": data.get("reported_at") or datetime.now(timezone.utc),
        }

        inserted_id = self.landslide_repo.create(doc)
        doc["_id"] = inserted_id

        # Trigger notification if created as ACTIVE
        if doc["is_active"]:
            self.activate_landslide(inserted_id)

        return doc

    def update_landslide(self, landslide_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if "lat" in updates or "lng" in updates:
            lat = float(updates.get("lat", 11.2500))
            lng = float(updates.get("lng", 76.9000))
            updates["location"] = {"type": "Point", "coordinates": [lng, lat]}

        if "status" in updates:
            updates["is_active"] = updates["status"].upper() == "ACTIVE"

        success = self.landslide_repo.update(landslide_id, updates)
        if success:
            return self.landslide_repo.get_by_id(landslide_id)
        return None

    def delete_landslide(self, landslide_id: str) -> bool:
        return self.landslide_repo.delete(landslide_id)

    def list_landslides(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = {}
        if status and status.upper() != "ALL":
            query["status"] = status.upper()
        return self.landslide_repo.find(query=query, sort=[("reported_at", -1)])
