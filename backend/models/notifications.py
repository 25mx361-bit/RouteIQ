"""
backend/models/notifications.py — Notification document model.

Collection: notifications

Schema
------
_id         : ObjectId
user_id     : str — recipient user id
title       : str
message     : str
type        : str — "alert" | "traffic_update" | "system" | "route_reminder"
is_read     : bool (default False)
metadata    : dict (optional)
created_at  : datetime
updated_at  : datetime

Indexes (created in database.py)
---------------------------------
  (user_id, created_at) COMPOUND (user_id ASC, created_at DESC)
  is_read               ASCENDING
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pymongo.database import Database
from pymongo import DESCENDING

from backend.models.base import BaseModel


class NotificationModel(BaseModel):
    COLLECTION = "notifications"
    REQUIRED_FIELDS = ["user_id", "title", "message"]

    @classmethod
    def insert(cls, db: Database, data: Dict[str, Any]):
        data.setdefault("is_read", False)
        data.setdefault("type", "traffic_update")
        data.setdefault("metadata", {})
        return super().insert(db, data)

    @classmethod
    def find_by_user(
        cls, db: Database, user_id: str, unread_only: bool = False, limit: int = 50
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"user_id": user_id}
        if unread_only:
            query["is_read"] = False
        return cls.find_many(
            db,
            query,
            sort=[("created_at", DESCENDING)],
            limit=limit,
        )

    @classmethod
    def mark_as_read(cls, db: Database, doc_id: str):
        return cls.update(db, doc_id, {"is_read": True})

    @classmethod
    def mark_all_as_read(cls, db: Database, user_id: str):
        return db[cls.COLLECTION].update_many(
            {"user_id": user_id, "is_read": False},
            {"$set": {"is_read": True, "updated_at": cls.utcnow()}},
        )
