"""
backend/repositories/model_log_repository.py — Model logs repository.
"""
from __future__ import annotations

from typing import Any, Dict, List
from backend.models.model_logs import ModelLogModel
from backend.repositories.base_repository import BaseRepository


class ModelLogRepository(BaseRepository[ModelLogModel]):
    model = ModelLogModel

    def get_model_history(self, model_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        docs = self.model.find_latest_by_model(self.db, model_name, limit=limit)
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return docs
