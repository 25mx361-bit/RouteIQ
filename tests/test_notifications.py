import sys
from pathlib import Path

current = Path(__file__).resolve()
for p in [current.parent, current.parent.parent]:
    if (p / "backend").exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

from backend.app import create_app
from backend.config.settings import TestingConfig
from backend.services.notification_service import NotificationService
from backend.database import get_db

def run_tests():
    print("=================================================================")
    print(" RouteIQ Phase 11: Notifications System Test Suite")
    print("=================================================================")
    
    app = create_app(TestingConfig)
    with app.app_context():
        db = get_db()
        svc = NotificationService(db)

        # 1. Create a notification
        notif = svc.create_notification(
            user_id="user_123",
            type="SYSTEM",
            title="Test Alert",
            message="This is a test notification."
        )
        assert notif is not None
        assert notif["title"] == "Test Alert"
        assert notif["user_id"] == "user_123"
        assert notif["is_read"] is False
        notif_id = str(notif["_id"])
        print(f" [PASS] Created notification: id={notif_id}, title='{notif['title']}'")

        # 2. Get unread notifications
        unreads = svc.get_user_notifications("user_123", unread_only=True)
        assert len(unreads) >= 1
        print(" [PASS] Retrieved unread notifications.")

        # 3. Mark as read
        success = svc.mark_as_read(notif_id, "user_123")
        assert success is True
        print(f" [PASS] Marked notification {notif_id} as read.")

        # 4. Verify it's no longer unread
        unreads_after = [n for n in svc.get_user_notifications("user_123", unread_only=True) if str(n["_id"]) == notif_id]
        assert len(unreads_after) == 0
        print(" [PASS] Verified notification is no longer in unread list.")

        # 5. Broadcast notification
        broadcast = svc.create_notification(
            user_id="broadcast_all",
            type="LANDSLIDE_ALERT",
            title="Broadcast Alert",
            message="Everyone sees this."
        )
        assert broadcast is not None
        print(" [PASS] Created broadcast notification.")

        # Verify user sees broadcast
        user_notifs = svc.get_user_notifications("user_123", unread_only=False)
        assert any(str(n["_id"]) == str(broadcast["_id"]) for n in user_notifs)
        print(" [PASS] Verified user receives broadcast_all notifications.")

        # 6. Mark all as read
        count = svc.mark_all_as_read("user_123")
        assert count >= 1
        print(f" [PASS] Marked all as read (affected {count} docs).")

        print("=================================================================")
        print(" [RESULT] >>> PASS <<< All Notification Tests Passed!")
        print("=================================================================")

if __name__ == "__main__":
    run_tests()
