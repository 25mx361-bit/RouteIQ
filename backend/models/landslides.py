"""
backend/models/landslides.py — Landslide Hazard & Road Blockage Document Model.

Collection: landslides

Schema:
  _id          : ObjectId
  title        : str
  risk_level   : str ("Low" | "Moderate" | "High" | "Severe" | "Critical")
  severity     : str ("CRITICAL" | "HIGH" | "MODERATE" | "LOW")
  status       : str ("ACTIVE" | "RESOLVED" | "MONITORING")
  is_active    : bool
  location     : dict (GeoJSON Point {"type": "Point", "coordinates": [lng, lat]})
  lat          : float
  lng          : float
  region_name  : str (e.g. "Western Ghats - Coonoor Ghat", "Valparai Hairpin Corridor")
  road_name    : str (e.g. "NH-181 Coonoor Ghat Road")
  radius_m     : float (affected blockade radius in meters)
  rainfall_mm  : float (triggering precipitation)
  reported_at  : datetime
  resolved_at  : datetime (optional)
  description  : str
  created_at   : datetime
  updated_at   : datetime
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pymongo.database import Database
from pymongo import DESCENDING

from backend.models.base import BaseModel


class LandslideModel(BaseModel):
    COLLECTION = "landslides"
    REQUIRED_FIELDS = ["title", "location", "reported_at"]

    @classmethod
    def insert(cls, db: Database, data: Dict[str, Any]):
        data.setdefault("is_active", True)
        data.setdefault("status", "ACTIVE")
        data.setdefault("risk_level", "High")
        data.setdefault("severity", "HIGH")
        data.setdefault("radius_m", 2500.0)
        data.setdefault("rainfall_mm", 0.0)
        data.setdefault("reported_at", cls.utcnow())

        loc = data.get("location", {})
        coords = loc.get("coordinates", [])
        if len(coords) >= 2:
            data.setdefault("lng", float(coords[0]))
            data.setdefault("lat", float(coords[1]))

        return super().insert(db, data)

    @classmethod
    def find_active(cls, db: Database) -> List[Dict[str, Any]]:
        return cls.find_many(
            db,
            {"$or": [{"is_active": True}, {"status": "ACTIVE"}]},
            sort=[("reported_at", DESCENDING)],
        )

    @classmethod
    def find_near(
        cls, db: Database, lng: float, lat: float, max_distance_m: float = 10000
    ) -> List[Dict[str, Any]]:
        """Find landslides near geographic coordinates."""
        query = {
            "location": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                    "$maxDistance": max_distance_m,
                }
            }
        }
        return cls.find_many(db, query)
