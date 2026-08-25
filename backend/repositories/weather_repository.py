"""
backend/repositories/weather_repository.py — Weather repository.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from backend.models.weather_data import WeatherDataModel
from backend.repositories.base_repository import BaseRepository


class WeatherRepository(BaseRepository[WeatherDataModel]):
    model = WeatherDataModel

    def get_nearest_weather(
        self,
        lat: float,
        lng: float,
        timestamp: datetime,
        tolerance_deg: float = 0.05,
    ) -> Optional[Dict[str, Any]]:
        doc = self.model.find_nearest(
            self.db, lat, lng, timestamp, tolerance_deg=tolerance_deg
        )
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def insert_batch(self, records: List[Dict[str, Any]]) -> int:
        return self.model.bulk_insert(self.db, records)
