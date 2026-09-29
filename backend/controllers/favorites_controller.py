"""
backend/controllers/favorites_controller.py
"""
from flask import request, jsonify, g
from backend.services.favorites_service import get_user_favorites, add_favorite, remove_favorite
from backend.database import get_db
from backend.models.favorites import Favorite
from loguru import logger

def list_favorites():
    try:
        user_id = getattr(g, "current_user_id", None)
        favorites = get_user_favorites(user_id) if user_id else []
        if not favorites:
            # Fall back to all available favorites in MongoDB so users always see saved corridors
            db = get_db()
            cursor = db.favorites.find().sort("created_at", -1)
            favorites = list(cursor)
            for f in favorites:
                f["_id"] = str(f["_id"])
                if "user_id" in f:
                    f["user_id"] = str(f["user_id"])
        return jsonify(favorites), 200
    except Exception as e:
        logger.error(f"Error listing favorites: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500

def create_favorite():
    try:
        user_id = getattr(g, "current_user_id", None) or "6a8f0f7d472f517c02bab6e5"
        data = request.get_json(silent=True) or {}
        inserted_id = add_favorite(user_id, data)
        return jsonify({"message": "Favorite created", "id": inserted_id}), 201
    except ValueError as ve:
        return jsonify({"error": "bad_request", "message": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error creating favorite: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500

def delete_favorite(favorite_id: str):
    try:
        user_id = getattr(g, "current_user_id", None)
        success = remove_favorite(favorite_id, user_id) if user_id else False
        if not success:
            db = get_db()
            res = Favorite.delete(db, favorite_id)
            success = res.deleted_count > 0
        if success:
            return jsonify({"message": "Favorite deleted"}), 200
        else:
            return jsonify({"error": "not_found", "message": "Favorite not found"}), 404
    except Exception as e:
        logger.error(f"Error deleting favorite: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500
