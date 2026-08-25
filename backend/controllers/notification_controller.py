from flask import Blueprint, request, jsonify
from backend.services.notification_service import NotificationService

# Initialize Service
# The blueprint isn't strictly needed in the controller if we use routes.py, but we'll export functions.

def get_user_notifications_controller():
    # In a real app, user_id comes from JWT token. We'll simulate with query param or default to "user_123"
    user_id = request.args.get("user_id", "user_123")
    unread_only = request.args.get("unread_only", "false").lower() == "true"
    
    svc = NotificationService()
    try:
        notifications = svc.get_user_notifications(user_id=user_id, unread_only=unread_only)
        return jsonify({"success": True, "notifications": notifications}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


def mark_as_read_controller(notification_id):
    user_id = request.args.get("user_id", "user_123")
    svc = NotificationService()
    try:
        success = svc.mark_as_read(notification_id, user_id)
        if success:
            return jsonify({"success": True, "message": "Notification marked as read"}), 200
        else:
            return jsonify({"success": False, "message": "Notification not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


def mark_all_as_read_controller():
    user_id = request.args.get("user_id", "user_123")
    svc = NotificationService()
    try:
        updated_count = svc.mark_all_as_read(user_id)
        return jsonify({"success": True, "message": f"{updated_count} notifications marked as read"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
