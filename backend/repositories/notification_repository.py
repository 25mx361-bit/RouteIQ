"""
backend/repositories/notification_repository.py — Notification repository.
"""
from __future__ import annotations

from typing import Any, Dict, List
from backend.models.notifications import NotificationModel
from backend.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[NotificationModel]):
    model = NotificationModel

    def get_user_notifications(
        self, user_id: str, unread_only: bool = False, limit: int = 50
    ) -> List[Dict[str, Any]]:
        docs = self.model.find_by_user(
            self.db, user_id, unread_only=unread_only, limit=limit
        )
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return docs

    def mark_as_read(self, notification_id: str) -> bool:
        res = self.model.mark_as_read(self.db, notification_id)
        return res.matched_count > 0

    def mark_all_user_notifications_read(self, user_id: str) -> int:
        res = self.model.mark_all_as_read(self.db, user_id)
        return res.modified_count
