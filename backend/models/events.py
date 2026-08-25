"""
backend/models/events.py — Traffic Events, Festivals, Marriages & Public Gatherings Model.

Collection: events

Supported Event Types:
  - FESTIVAL
  - MARRIAGE
  - SPORTS_EVENT
  - POLITICAL_EVENT
  - SCHOOL_EVENT
  - COLLEGE_EVENT
  - PUBLIC_EVENT
  - OTHER

Schema:
  _id            : ObjectId
  title          : str
  event_type     : str (FESTIVAL | MARRIAGE | SPORTS_EVENT | POLITICAL_EVENT | SCHOOL_EVENT | COLLEGE_EVENT | PUBLIC_EVENT | OTHER)
  description    : str
  venue_name     : str
  road_name      : str
  location       : dict (GeoJSON Point: {"type": "Point", "coordinates": [lng, lat]})
  lat            : float
  lng            : float
  radius_m       : float (affected bottleneck radius)
  expected_crowd : int
  impact_level   : str ("LOW" | "MEDIUM" | "HIGH" | "CRITICAL")
  start_time     : datetime
  end_time       : datetime
  status         : str ("ACTIVE" | "UPCOMING" | "EXPIRED" | "CANCELLED")
  is_active      : bool
  created_at     : datetime
  updated_at     : datetime
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pymongo.database import Database
from pymongo import DESCENDING

from backend.models.base import BaseModel

VALID_EVENT_TYPES = {
    "FESTIVAL",
    "MARRIAGE",
    "SPORTS_EVENT",
    "POLITICAL_EVENT",
    "SCHOOL_EVENT",
    "COLLEGE_EVENT",
    "PUBLIC_EVENT",
    "OTHER",
}

VALID_IMPACT_LEVELS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


class EventModel(BaseModel):
    COLLECTION = "events"
    REQUIRED_FIELDS = ["title", "event_type", "location", "start_time"]

    @classmethod
    def insert(cls, db: Database, data: Dict[str, Any]):
        e_type = str(data.get("event_type", "OTHER")).upper()
        if e_type not in VALID_EVENT_TYPES:
            e_type = "OTHER"
        data["event_type"] = e_type

        imp = str(data.get("impact_level", "MEDIUM")).upper()
        if imp not in VALID_IMPACT_LEVELS:
            imp = "MEDIUM"
        data["impact_level"] = imp

        data.setdefault("expected_crowd", 500)
        data.setdefault("radius_m", 1500.0)
        data.setdefault("is_active", True)
        data.setdefault("status", "ACTIVE")
        data.setdefault("timestamp", data.get("start_time") or cls.utcnow())

        # Ensure lat & lng are populated alongside GeoJSON location
        loc = data.get("location", {})
        coords = loc.get("coordinates", [])
        if len(coords) >= 2:
            data.setdefault("lng", float(coords[0]))
            data.setdefault("lat", float(coords[1]))

        return super().insert(db, data)

    @classmethod
    def find_active(
        cls, db: Database, target_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Return events that are currently active around target_time."""
        check_time = target_time or cls.utcnow()
        query = {
            "is_active": True,
            "start_time": {"$lte": check_time},
            "$or": [
                {"end_time": {"$gte": check_time}},
                {"end_time": None},
            ],
        }
        return cls.find_many(db, query, sort=[("start_time", DESCENDING)])

    @classmethod
    def find_by_type(cls, db: Database, event_type: str) -> List[Dict[str, Any]]:
        return cls.find_many(
            db,
            {"event_type": event_type.upper()},
            sort=[("start_time", DESCENDING)],
        )
