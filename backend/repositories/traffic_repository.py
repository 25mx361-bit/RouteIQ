"""
backend/repositories/traffic_repository.py — Traffic data repository.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from backend.models.traffic_data import TrafficDataModel
from backend.repositories.base_repository import BaseRepository


class TrafficRepository(BaseRepository[TrafficDataModel]):
    model = TrafficDataModel

    def get_segment_history(
        self,
        segment_id: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        docs = self.model.find_by_segment(
            self.db, segment_id, start=start, end=end, limit=limit
        )
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return docs

    def get_latest_reading(self, segment_id: str) -> Optional[Dict[str, Any]]:
        doc = self.model.latest_for_segment(self.db, segment_id)
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def insert_batch(self, records: List[Dict[str, Any]]) -> int:
        return self.model.bulk_insert(self.db, records)
