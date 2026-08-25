"""
backend/repositories/system_log_repository.py — System logs repository.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from backend.models.system_logs import SystemLogModel
from backend.repositories.base_repository import BaseRepository


class SystemLogRepository(BaseRepository[SystemLogModel]):
    model = SystemLogModel

    def log(
        self,
        level: str,
        source: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> str:
        res = self.model.log(
            self.db,
            level=level,
            source=source,
            message=message,
            details=details,
            user_id=user_id,
        )
        return str(res.inserted_id)

    def get_recent_logs(
        self, level: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        docs = self.model.find_recent(self.db, level=level, limit=limit)
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return docs
