"""
backend/repositories/route_repository.py — Route repository.
"""
from __future__ import annotations

from typing import Any, Dict, List
from backend.models.routes import RouteModel
from backend.repositories.base_repository import BaseRepository


class RouteRepository(BaseRepository[RouteModel]):
    model = RouteModel

    def get_by_search_id(self, search_id: str) -> List[Dict[str, Any]]:
        docs = self.model.find_by_search_id(self.db, search_id)
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return docs

    def get_user_routes(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        docs = self.model.find_by_user(self.db, user_id, limit=limit)
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return docs
