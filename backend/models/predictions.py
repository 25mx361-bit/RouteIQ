"""
backend/models/predictions.py — Prediction document model.

Collection: predictions

Schema
------
_id               : ObjectId
user_id           : str — user making prediction request
source            : dict {"lat": float, "lng": float, "label": str}
destination       : dict {"lat": float, "lng": float, "label": str}
travel_datetime   : datetime — target travel date & time
predicted_traffic : dict or list — PatchTST forecasted values
congestion_level  : str — "Low" | "Medium" | "High"
recommendation    : dict — recommended route details selected by CatBoost
alternative_routes: list[dict] — alternative routes with evaluation metrics
weather_context   : dict — weather features used during prediction
execution_time_ms : float — inference duration
created_at        : datetime
updated_at        : datetime

Indexes (created in database.py)
---------------------------------
  user_id                        ASCENDING
  (user_id, created_at)          COMPOUND (user_id ASC, created_at DESC)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pymongo.database import Database
from pymongo import DESCENDING

from backend.models.base import BaseModel


class PredictionModel(BaseModel):
    COLLECTION = "predictions"
    REQUIRED_FIELDS = [
        "source",
        "destination",
        "travel_datetime",
        "congestion_level",
        "recommendation",
    ]

    @classmethod
    def insert(cls, db: Database, data: Dict[str, Any]):
        data.setdefault("alternative_routes", [])
        data.setdefault("weather_context", {})
        return super().insert(db, data)

    @classmethod
    def find_by_user(
        cls, db: Database, user_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        return cls.find_many(
            db,
            {"user_id": user_id},
            sort=[("created_at", DESCENDING)],
            limit=limit,
        )
