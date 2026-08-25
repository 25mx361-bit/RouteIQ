"""
backend/models/routes.py — Route document model.

Collection: routes

Schema
------
_id               : ObjectId
search_id         : str — unique identifier for search query session
route_id          : str — identifier within search session (e.g., "route_0", "route_1")
user_id           : str (optional)
source            : dict {"lat": float, "lng": float, "label": str}
destination       : dict {"lat": float, "lng": float, "label": str}
distance_m        : float — distance in meters
distance_km       : float — distance in kilometers
duration_s        : float — duration in seconds
duration_min      : float — duration in minutes
geometry          : dict or list — GeoJSON LineString coordinates
segments          : list[dict] — road segment steps
is_recommended    : bool — whether selected as primary recommended route
route_rank        : int — (0=primary, 1=alt1, 2=alt2)
source_label      : str
destination_label : str
fetched_at        : datetime
created_at        : datetime
updated_at        : datetime
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pymongo.database import Database
from pymongo import ASCENDING, DESCENDING

from backend.models.base import BaseModel


class RouteModel(BaseModel):
    COLLECTION = "routes"
    REQUIRED_FIELDS = ["source", "destination", "distance_m", "duration_s"]

    @classmethod
    def insert(cls, db: Database, data: Dict[str, Any]):
        now = cls.utcnow()
        data.setdefault("fetched_at", now)
        data.setdefault("profile", "driving-car")
        data.setdefault("route_rank", 0)
        data.setdefault("is_recommended", False)
        
        # Calculate derived distance and duration if not provided
        if "distance_km" not in data and "distance_m" in data:
            data["distance_km"] = round(float(data["distance_m"]) / 1000.0, 2)
        if "duration_min" not in data and "duration_s" in data:
            data["duration_min"] = round(float(data["duration_s"]) / 60.0, 1)

        # Text search fields
        if isinstance(data.get("source"), dict):
            data.setdefault("source_label", data["source"].get("label", ""))
        if isinstance(data.get("destination"), dict):
            data.setdefault("destination_label", data["destination"].get("label", ""))

        return super().insert(db, data)

    @classmethod
    def find_by_search_id(
        cls, db: Database, search_id: str
    ) -> List[Dict[str, Any]]:
        return cls.find_many(
            db,
            {"search_id": search_id},
            sort=[("route_rank", ASCENDING)],
        )

    @classmethod
    def find_by_user(
        cls, db: Database, user_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        return cls.find_many(
            db,
            {"user_id": user_id},
            sort=[("fetched_at", DESCENDING)],
            limit=limit,
        )
