"""
backend/models/system_logs.py — System and API audit logs model with automatic TTL expiry.

Collection: system_logs

Schema
------
_id         : ObjectId
level       : str — "INFO" | "WARNING" | "ERROR" | "DEBUG" | "CRITICAL"
source      : str — module or endpoint name (e.g. "api.v1.prediction")
message     : str
details     : dict — extra payload/traceback
user_id     : str (optional)
timestamp   : datetime
created_at  : datetime
updated_at  : datetime

Indexes (created in database.py)
---------------------------------
  level         ASCENDING
  timestamp     DESCENDING
  timestamp     TTL Index (auto-expire after 30 days)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pymongo.database import Database
from pymongo import DESCENDING

from backend.models.base import BaseModel


class SystemLogModel(BaseModel):
    COLLECTION = "system_logs"
    REQUIRED_FIELDS = ["level", "source", "message"]

    @classmethod
    def insert(cls, db: Database, data: Dict[str, Any]):
        now = cls.utcnow()
        data.setdefault("timestamp", now)
        data.setdefault("details", {})
        return super().insert(db, data)

    @classmethod
    def log(
        cls,
        db: Database,
        level: str,
        source: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ):
        data = {
            "level": level.upper(),
            "source": source,
            "message": message,
            "details": details or {},
            "user_id": user_id,
        }
        return cls.insert(db, data)

    @classmethod
    def find_recent(
        cls, db: Database, level: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        query = {"level": level.upper()} if level else {}
        return cls.find_many(
            db,
            query,
            sort=[("timestamp", DESCENDING)],
            limit=limit,
        )
