"""
backend/models/search_history.py — Search History document model.

Collection: search_history

Schema
------
_id               : ObjectId
user_id           : str — requesting user id
source_query      : str — user search text
destination_query : str — user search text
source_coords     : dict {"lat": float, "lng": float}
dest_coords       : dict {"lat": float, "lng": float}
travel_datetime   : datetime
searched_at       : datetime
created_at        : datetime
updated_at        : datetime

Indexes (created in database.py)
---------------------------------
  (user_id, searched_at) COMPOUND (user_id ASC, searched_at DESC)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pymongo.database import Database
from pymongo import DESCENDING

from backend.models.base import BaseModel


class SearchHistoryModel(BaseModel):
    COLLECTION = "search_history"
    REQUIRED_FIELDS = ["user_id", "source_query", "destination_query"]

    @classmethod
    def insert(cls, db: Database, data: Dict[str, Any]):
        now = cls.utcnow()
        data.setdefault("searched_at", now)
        return super().insert(db, data)

    @classmethod
    def find_by_user(
        cls, db: Database, user_id: str, limit: int = 15
    ) -> List[Dict[str, Any]]:
        return cls.find_many(
            db,
            {"user_id": user_id},
            sort=[("searched_at", DESCENDING)],
            limit=limit,
        )

    @classmethod
    def clear_user_history(cls, db: Database, user_id: str):
        return db[cls.COLLECTION].delete_many({"user_id": user_id})
