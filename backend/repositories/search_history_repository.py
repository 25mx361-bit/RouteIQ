"""
backend/repositories/search_history_repository.py — Search history repository.
"""
from __future__ import annotations

from typing import Any, Dict, List
from backend.models.search_history import SearchHistoryModel
from backend.repositories.base_repository import BaseRepository


class SearchHistoryRepository(BaseRepository[SearchHistoryModel]):
    model = SearchHistoryModel

    def get_user_searches(self, user_id: str, limit: int = 15) -> List[Dict[str, Any]]:
        docs = self.model.find_by_user(self.db, user_id, limit=limit)
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return docs

    def clear_history(self, user_id: str) -> int:
        res = self.model.clear_user_history(self.db, user_id)
        return res.deleted_count
