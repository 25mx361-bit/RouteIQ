"""
backend/repositories/prediction_repository.py — Prediction repository.
"""
from __future__ import annotations

from typing import Any, Dict, List
from backend.models.predictions import PredictionModel
from backend.repositories.base_repository import BaseRepository


class PredictionRepository(BaseRepository[PredictionModel]):
    model = PredictionModel

    def get_user_history(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        docs = self.model.find_by_user(self.db, user_id, limit=limit)
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return docs
