"""
backend/repositories/landslide_repository.py — Landslide alert repository.
"""
from __future__ import annotations

from typing import Any, Dict, List
from backend.models.landslides import LandslideModel
from backend.repositories.base_repository import BaseRepository


class LandslideRepository(BaseRepository[LandslideModel]):
    model = LandslideModel

    def get_active_landslides(self) -> List[Dict[str, Any]]:
        docs = self.model.find_active(self.db)
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return docs

    def get_nearby_landslides(
        self, lng: float, lat: float, max_distance_m: float = 10000
    ) -> List[Dict[str, Any]]:
        docs = self.model.find_near(self.db, lng, lat, max_distance_m)
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return docs
