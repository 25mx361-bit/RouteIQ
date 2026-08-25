"""
backend/controllers/admin_users_controller.py — Admin user management endpoints.

Protected by @require_admin in routes.
"""
from __future__ import annotations

from flask import request, jsonify, g
from loguru import logger
from bson import ObjectId
from backend.database import get_db
from backend.models.user import UserModel


def list_users():
    """
    GET /api/admin/users
    Returns all users (paginated, 100 max). Admin only.
    """
    db = get_db()
    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(int(request.args.get("limit", 100)), 200)
        skip = (page - 1) * limit

        collection = db[UserModel.COLLECTION]
        cursor = collection.find({}, {"password_hash": 0}).sort("created_at", -1).skip(skip).limit(limit)
        total = collection.count_documents({})

        users = []
        for u in cursor:
            u["_id"] = str(u["_id"])
            u.pop("password_hash", None)
            users.append(u)

        return jsonify({
            "success": True,
            "users": users,
            "total": total,
            "page": page,
            "limit": limit,
        }), 200

    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500


def update_user_role(user_id: str):
    """
    PUT /api/admin/users/<user_id>/role
    Body: { "role": "admin" | "user" }
    """
    db = get_db()
    try:
        body = request.get_json(silent=True) or {}
        new_role = body.get("role", "").strip().lower()

        if new_role not in {"admin", "user"}:
            return jsonify({
                "error": "bad_request",
                "message": "Role must be 'admin' or 'user'.",
            }), 400

        # Prevent self-demotion
        if str(g.current_user_id) == user_id and new_role != "admin":
            return jsonify({
                "error": "bad_request",
                "message": "You cannot demote your own admin account.",
            }), 400

        try:
            oid = ObjectId(user_id)
        except Exception:
            return jsonify({"error": "bad_request", "message": "Invalid user ID."}), 400

        from backend.models.base import BaseModel
        now = BaseModel.utcnow()
        result = db[UserModel.COLLECTION].update_one(
            {"_id": oid},
            {"$set": {"role": new_role, "updated_at": now}},
        )

        if result.matched_count == 0:
            return jsonify({"error": "not_found", "message": "User not found."}), 404

        logger.info(f"Admin {g.current_user_id} changed user {user_id} role to '{new_role}'")
        return jsonify({"success": True, "message": f"User role updated to '{new_role}'."}), 200

    except Exception as e:
        logger.error(f"Failed to update user role: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500


def deactivate_user(user_id: str):
    """
    PUT /api/admin/users/<user_id>/deactivate
    Sets is_active = False on the user account.
    """
    db = get_db()
    try:
        if str(g.current_user_id) == user_id:
            return jsonify({"error": "bad_request", "message": "Cannot deactivate your own account."}), 400

        try:
            oid = ObjectId(user_id)
        except Exception:
            return jsonify({"error": "bad_request", "message": "Invalid user ID."}), 400

        from backend.models.base import BaseModel
        result = db[UserModel.COLLECTION].update_one(
            {"_id": oid},
            {"$set": {"is_active": False, "updated_at": BaseModel.utcnow()}},
        )

        if result.matched_count == 0:
            return jsonify({"error": "not_found", "message": "User not found."}), 404

        logger.info(f"Admin {g.current_user_id} deactivated user {user_id}")
        return jsonify({"success": True, "message": "User account deactivated."}), 200

    except Exception as e:
        logger.error(f"Failed to deactivate user: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500


def get_admin_stats():
    """
    GET /api/admin/stats
    Returns summary statistics for the Admin Dashboard.
    """
    db = get_db()
    try:
        from datetime import datetime, timezone
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        total_users = db["users"].count_documents({})
        active_events = db["events"].count_documents({"status": "ACTIVE"})
        active_landslides = db["landslides"].count_documents({"status": "ACTIVE"})
        routes_today = db["routes"].count_documents({"created_at": {"$gte": today_start}})
        total_notifications = db["notifications"].count_documents({})
        unread_notifications = db["notifications"].count_documents({"is_read": False})

        # Scheduler status
        try:
            from backend.scheduler.scheduler import get_scheduler_status
            scheduler = get_scheduler_status()
            scheduler_running = scheduler.get("is_running", False)
        except Exception:
            scheduler_running = False

        return jsonify({
            "success": True,
            "stats": {
                "total_users": total_users,
                "active_events": active_events,
                "active_landslides": active_landslides,
                "routes_searched_today": routes_today,
                "total_notifications": total_notifications,
                "unread_notifications": unread_notifications,
                "scheduler_running": scheduler_running,
            },
        }), 200

    except Exception as e:
        logger.error(f"Failed to get admin stats: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500


def get_system_logs():
    """
    GET /api/admin/logs
    Query params: level, source, date_from, date_to, limit, page
    """
    db = get_db()
    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(int(request.args.get("limit", 50)), 200)
        skip = (page - 1) * limit

        query = {}
        level = request.args.get("level", "").upper()
        source = request.args.get("source", "").strip()
        date_from = request.args.get("date_from", "")
        date_to = request.args.get("date_to", "")

        if level:
            query["level"] = level
        if source:
            query["source"] = {"$regex": source, "$options": "i"}
        if date_from or date_to:
            from datetime import datetime
            dt_filter = {}
            if date_from:
                dt_filter["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                dt_filter["$lte"] = datetime.fromisoformat(date_to)
            query["logged_at"] = dt_filter

        collection = db["system_logs"]
        total = collection.count_documents(query)
        cursor = collection.find(query).sort("logged_at", -1).skip(skip).limit(limit)

        logs = []
        for log in cursor:
            log["_id"] = str(log["_id"])
            logs.append(log)

        return jsonify({
            "success": True,
            "logs": logs,
            "total": total,
            "page": page,
            "limit": limit,
        }), 200

    except Exception as e:
        logger.error(f"Failed to fetch system logs: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500
