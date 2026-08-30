"""
backend/controllers/user_controller.py
"""
from flask import jsonify, request, g
from pymongo import DESCENDING
from backend.database import get_db
from loguru import logger
from backend.models.favorites import Favorite

def get_user_stats():
    try:
        user_id = g.current_user_id
        db = get_db()
        
        total_searches = db.routes.count_documents({"user_id": user_id})
        total_predictions = db.predictions.count_documents({"user_id": user_id})
        total_recommended_routes = db.routes.count_documents({"user_id": user_id, "is_recommended": True})
        total_favorites = Favorite.count(db, {"user_id": user_id})
        
        return jsonify({
            "total_searches": total_searches,
            "total_predictions": total_predictions,
            "total_recommended_routes": total_recommended_routes,
            "total_favorites": total_favorites
        }), 200
    except Exception as e:
        logger.error(f"Error in get_user_stats: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500

def get_user_history():
    try:
        user_id = g.current_user_id
        limit = int(request.args.get("limit", 20))
        page = int(request.args.get("page", 1))
        skip = (page - 1) * limit
        
        db = get_db()
        query = {"user_id": user_id}
        
        total = db.routes.count_documents(query)
        cursor = db.routes.find(query).sort("created_at", DESCENDING).skip(skip).limit(limit)
        
        history = []
        for doc in cursor:
            history.append({
                "_id": str(doc["_id"]),
                "source_label": doc.get("source_label"),
                "destination_label": doc.get("destination_label"),
                "created_at": doc.get("created_at"),
                "is_recommended": doc.get("is_recommended"),
                "distance_km": doc.get("distance_km"),
                "duration_min": doc.get("duration_min")
            })
            
        return jsonify({
            "history": history,
            "total": total,
            "page": page
        }), 200
    except Exception as e:
        logger.error(f"Error in get_user_history: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500

def get_current_user_profile():
    try:
        user_id = g.current_user_id
        db = get_db()
        
        from bson import ObjectId
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "not_found", "message": "User not found"}), 404
            
        if "password_hash" in user:
            del user["password_hash"]
        user["_id"] = str(user["_id"])
        
        return jsonify(user), 200
    except Exception as e:
        logger.error(f"Error in get_current_user_profile: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500
