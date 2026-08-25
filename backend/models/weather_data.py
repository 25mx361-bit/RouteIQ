"""
backend/models/weather_data.py — Weather data document model.

Collection: weather_data

Schema
------
_id         : ObjectId
timestamp   : datetime  — UTC time of reading / forecast hour
lat         : float     — location latitude
lng         : float     — location longitude
temperature : float     — degrees Celsius
rainfall_mm : float     — precipitation in mm
humidity_pct: float     — relative humidity %
visibility_m: float     — visibility in metres
wind_speed  : float     — km/h
condition   : str       — e.g. "clear", "rain", "fog"
source      : str       — "open_meteo" | "manual"
created_at  : datetime
updated_at  : datetime

Indexes (created in database.py)
---------------------------------
  (timestamp, lat, lng) COMPOUND  — primary lookup
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pymongo import ASCENDING, DESCENDING
from pymongo.database import Database

from backend.models.base import BaseModel


class WeatherDataModel(BaseModel):
    COLLECTION = "weather_data"
    REQUIRED_FIELDS = ["timestamp", "lat", "lng", "temperature", "source"]

    @classmethod
    def insert(cls, db: Database, data: Dict[str, Any]):
        data.setdefault("condition", "unknown")
        data.setdefault("rainfall_mm", 0.0)
        data.setdefault("wind_speed", 0.0)
        return super().insert(db, data)

    @classmethod
    def find_nearest(
        cls,
        db: Database,
        lat: float,
        lng: float,
        timestamp: datetime,
        tolerance_deg: float = 0.05,
    ) -> Optional[Dict[str, Any]]:
        """
        Return the closest weather record spatially and temporally.
        Uses a simple bounding-box approach (no 2dsphere index needed).
        """
        return db[cls.COLLECTION].find_one(
            {
                "lat":  {"$gte": lat - tolerance_deg, "$lte": lat + tolerance_deg},
                "lng":  {"$gte": lng - tolerance_deg, "$lte": lng + tolerance_deg},
                "timestamp": {"$lte": timestamp},
            },
            sort=[("timestamp", DESCENDING)],
        )

    @classmethod
    def bulk_insert(cls, db: Database, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        now = cls.utcnow()
        for r in records:
            r.setdefault("created_at", now)
            r.setdefault("updated_at", now)
            r.setdefault("condition", "unknown")
            r.setdefault("rainfall_mm", 0.0)
        result = db[cls.COLLECTION].insert_many(records, ordered=False)
        return len(result.inserted_ids)
