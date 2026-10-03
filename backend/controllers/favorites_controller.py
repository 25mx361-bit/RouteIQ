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
        if not user_id:
            return jsonify([]), 200
        favorites = get_user_favorites(str(user_id))
        return jsonify(favorites), 200
    except Exception as e:
        logger.error(f"Error listing favorites: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500

def create_favorite():
    try:
        user_id = getattr(g, "current_user_id", None)
        if not user_id:
            return jsonify({"error": "unauthorized", "message": "Sign in required to save favorites."}), 401
        data = request.get_json(silent=True) or {}
        inserted_id = add_favorite(str(user_id), data)
        return jsonify({"message": "Favorite created", "id": inserted_id}), 201
    except ValueError as ve:
        return jsonify({"error": "bad_request", "message": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error creating favorite: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500

def delete_favorite(favorite_id: str):
    try:
        user_id = getattr(g, "current_user_id", None)
        if not user_id:
            return jsonify({"error": "unauthorized", "message": "Sign in required."}), 401
        success = remove_favorite(favorite_id, str(user_id))
        if success:
            return jsonify({"message": "Favorite deleted"}), 200
        else:
            return jsonify({"error": "not_found", "message": "Favorite not found"}), 404
    except Exception as e:
        logger.error(f"Error deleting favorite: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500
