"""
backend/repositories/event_repository.py — Event Repository wrapping EventModel PyMongo calls.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from bson import ObjectId
from pymongo import DESCENDING

from backend.models.events import EventModel
from backend.repositories.base_repository import BaseRepository


class EventRepository(BaseRepository[EventModel]):
    model = EventModel

    def get_active_events(self, target_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        docs = self.model.find_active(self.db, target_time)
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return docs

    def get_nearby_events(
        self, lng: float, lat: float, max_distance_m: float = 5000
    ) -> List[Dict[str, Any]]:
        docs = self.model.find_near(self.db, lng, lat, max_distance_m)
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return docs

    def filter_events(
        self,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        date_str: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if event_type and event_type.upper() != "ALL":
            query["event_type"] = event_type.upper()
        if status and status.upper() != "ALL":
            query["status"] = status.upper()

        if date_str:
            try:
                day_start = datetime.fromisoformat(f"{date_str}T00:00:00")
                day_end = datetime.fromisoformat(f"{date_str}T23:59:59")
                query["$or"] = [
                    {"start_time": {"$gte": day_start, "$lte": day_end}},
                    {"start_time": {"$lte": day_start}, "end_time": {"$gte": day_start}},
                ]
            except Exception:
                pass

        docs = self.find(query=query, sort=[("start_time", DESCENDING)], limit=limit)
        return docs
