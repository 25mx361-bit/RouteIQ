"""
backend/models/traffic_data.py — Traffic data document model.

Collection: traffic_data

Schema
------
_id         : ObjectId
segment_id  : str       — road segment identifier (e.g. TomTom segment hash)
road_id     : str       — human-readable road name / ID
timestamp   : datetime  — UTC timestamp of the reading
speed_kmh   : float     — observed/recorded vehicle speed in km/h
free_flow_speed: float  — free-flow reference speed for this segment
current_travel_time: int — seconds
free_flow_travel_time: int — seconds
confidence  : float     — data confidence score [0–1]
road_closure: bool      — whether segment is closed
source      : str       — "tomtom" | "manual" | "simulated"
lat         : float     — segment midpoint latitude
lng         : float     — segment midpoint longitude
created_at  : datetime
updated_at  : datetime

Indexes (created in database.py)
---------------------------------
  (segment_id, timestamp) COMPOUND  — primary time-series lookup
  timestamp               DESCENDING
  road_id                 ASCENDING
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pymongo.database import Database
from pymongo import ASCENDING, DESCENDING

from backend.models.base import BaseModel


class TrafficDataModel(BaseModel):
    COLLECTION = "traffic_data"
    REQUIRED_FIELDS = ["segment_id", "timestamp", "speed_kmh", "source"]

    @classmethod
    def insert(cls, db: Database, data: Dict[str, Any]):
        data.setdefault("road_closure", False)
        data.setdefault("confidence", 1.0)
        return super().insert(db, data)

    @classmethod
    def find_by_segment(
        cls,
        db: Database,
        segment_id: str,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """Return time-ordered traffic records for a given segment."""
        query: Dict[str, Any] = {"segment_id": segment_id}
        if start or end:
            query["timestamp"] = {}
            if start:
                query["timestamp"]["$gte"] = start
            if end:
                query["timestamp"]["$lte"] = end
        return cls.find_many(
            db, query, sort=[("timestamp", ASCENDING)], limit=limit
        )

    @classmethod
    def latest_for_segment(
        cls, db: Database, segment_id: str
    ) -> Optional[Dict[str, Any]]:
        """Return the most recent record for a segment."""
        docs = cls.find_many(
            db, {"segment_id": segment_id},
            sort=[("timestamp", DESCENDING)],
            limit=1,
        )
        return docs[0] if docs else None

    @classmethod
    def bulk_insert(cls, db: Database, records: List[Dict[str, Any]]) -> int:
        """Insert many records at once; returns count inserted."""
        if not records:
            return 0
        now = cls.utcnow()
        for r in records:
            r.setdefault("created_at", now)
            r.setdefault("updated_at", now)
            r.setdefault("road_closure", False)
            r.setdefault("confidence", 1.0)
        result = db[cls.COLLECTION].insert_many(records, ordered=False)
        return len(result.inserted_ids)
