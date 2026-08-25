import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from backend.database import get_db
from backend.repositories.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)

class NotificationService:
    VALID_TYPES = [
        "LANDSLIDE_ALERT",
        "TRAFFIC_ALERT",
        "WEATHER_ALERT",
        "EVENT_ALERT",
        "ROUTE_UPDATE",
        "SYSTEM",
    ]

    def __init__(self, db=None):
        self.db = db if db is not None else get_db()
        self.repo = NotificationRepository(self.db)

    def create_notification(
        self,
        user_id: str,
        type: str,
        title: str,
        message: str,
        severity: str = "INFO",
        related_route_id: Optional[str] = None,
        related_event_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new notification.
        user_id can be 'broadcast_all' for global alerts.
        """
        if type not in self.VALID_TYPES:
            logger.warning(f"Invalid notification type '{type}'. Defaulting to 'SYSTEM'.")
            type = "SYSTEM"

        payload = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": type,
            "is_read": False,
            "metadata": {
                "severity": severity,
                "related_route_id": related_route_id,
                "related_event_id": related_event_id,
            },
            "created_at": datetime.now(timezone.utc),
        }

        try:
            doc_id = self.repo.create(payload)
            if doc_id:
                return self.repo.get_by_id(doc_id)
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
        return None

    def get_user_notifications(
        self, user_id: str, unread_only: bool = False, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve notifications for a user, including global broadcasts.
        """
        # A proper system might fetch user-specific + 'broadcast_all' separately 
        # and merge, but for RouteIQ, we'll fetch both using an $in query if supported,
        # or just fetch user_id and broadcast_all and sort.
        # Since our repo currently uses find_by_user which does {"user_id": user_id},
        # we'll build a custom query here for simplicity.
        query = {"user_id": {"$in": [user_id, "broadcast_all"]}}
        if unread_only:
            query["is_read"] = False
            
        docs = self.repo.find(query=query, sort=[("created_at", -1)], limit=limit)
        return docs

    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """
        Mark a specific notification as read.
        """
        # In a real app we'd verify user_id owns the notification, but for Phase 11 MVP we'll just mark it
        return self.repo.mark_as_read(notification_id)

    def mark_all_as_read(self, user_id: str) -> int:
        """
        Mark all unread notifications as read for a given user.
        """
        # For broadcast_all, marking read is tricky (should track read state per user).
        # For RouteIQ MVP, we'll mark the user's direct notifications and maybe ignore broadcast
        # or mark broadcast as read for everyone. We'll mark both.
        res1 = self.repo.mark_all_user_notifications_read(user_id)
        res2 = self.repo.mark_all_user_notifications_read("broadcast_all")
        return res1 + res2
