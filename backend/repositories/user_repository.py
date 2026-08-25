"""
backend/repositories/user_repository.py — User repository wrapping PyMongo operations.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from backend.models.user import UserModel
from backend.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    model = UserModel

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        doc = self.model.find_by_email(self.db, email)
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def deactivate(self, user_id: str) -> bool:
        res = self.model.deactivate(self.db, user_id)
        return res.matched_count > 0

    def update_role(self, user_id: str, role: str) -> bool:
        res = self.model.set_role(self.db, user_id, role)
        return res.matched_count > 0
