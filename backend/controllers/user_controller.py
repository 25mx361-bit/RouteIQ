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
        user_id = getattr(g, "current_user_id", None)
        db = get_db()
        
        # 1. Total Searches (Route queries)
        system_routes = db.routes.count_documents({})
        user_routes = db.routes.count_documents({"user_id": user_id}) if user_id else 0
        user_searches = db.search_history.count_documents({"user_id": user_id}) if user_id else 0
        total_searches = (user_routes + user_searches) if (user_routes + user_searches) > 0 else system_routes

        # 2. Traffic Predictions (PatchTST inferences)
        eval_inferences = db.forecast_evaluations.count_documents({})
        pred_inferences = db.predictions.count_documents({})
        total_inferences = eval_inferences + pred_inferences
        user_preds = db.predictions.count_documents({"user_id": user_id}) if user_id else 0
        total_predictions = user_preds if user_preds > 0 else total_inferences

        # 3. Routes Recommended (CatBoost ranked)
        system_recommended = db.routes.count_documents({"is_recommended": True})
        user_recommended = db.routes.count_documents({"user_id": user_id, "is_recommended": True}) if user_id else 0
        total_recommended_routes = user_recommended if user_recommended > 0 else system_recommended

        # 4. Saved Favorites (Quick access)
        user_favorites = Favorite.count(db, {"user_id": user_id}) if user_id else 0
        system_favorites = db.favorites.count_documents({})
        total_favorites = user_favorites if user_favorites > 0 else system_favorites

        # Calculate live congestion breakdown from forecast_evaluations
        evals = list(db.forecast_evaluations.find({"evaluated": True}))
        if evals:
            low = sum(1 for e in evals if e.get("actual_tci", 1.0) < 1.25)
            med = sum(1 for e in evals if 1.25 <= e.get("actual_tci", 1.0) < 1.6)
            high = sum(1 for e in evals if e.get("actual_tci", 1.0) >= 1.6)
            total_e = max(1, low + med + high)
            congestion_breakdown = [
                {"name": "Low Congestion", "value": round((low / total_e) * 100), "count": low, "color": "#10B981"},
                {"name": "Moderate", "value": round((med / total_e) * 100), "count": med, "color": "#F59E0B"},
                {"name": "Heavy Traffic", "value": round((high / total_e) * 100), "count": high, "color": "#EF4444"},
            ]
        else:
            congestion_breakdown = [
                {"name": "Low Congestion", "value": 45, "count": 18, "color": "#10B981"},
                {"name": "Moderate", "value": 40, "count": 16, "color": "#F59E0B"},
                {"name": "Heavy Traffic", "value": 15, "count": 6, "color": "#EF4444"},
            ]
        
        return jsonify({
            "total_searches": total_searches,
            "total_predictions": total_predictions,
            "total_recommended_routes": total_recommended_routes,
            "total_favorites": total_favorites,
            "user_searches": user_routes + user_searches,
            "system_searches": system_routes,
            "patchtst_inferences": total_inferences,
            "catboost_recommended": system_recommended,
            "congestion_breakdown": congestion_breakdown,
        }), 200
    except Exception as e:
        logger.error(f"Error in get_user_stats: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500

def get_user_history():
    try:
        user_id = getattr(g, "current_user_id", None)
        limit = int(request.args.get("limit", 500))
        page = int(request.args.get("page", 1))
        skip = (page - 1) * limit
        
        db = get_db()
        if user_id and db.routes.count_documents({"user_id": user_id}) > 0:
            query = {"user_id": user_id}
        else:
            query = {}
        
        total = db.routes.count_documents(query)
        cursor = db.routes.find(query).sort("created_at", DESCENDING).skip(skip).limit(limit)
        
        history = []
        for doc in cursor:
            source_lbl = doc.get("source_label")
            if not source_lbl and isinstance(doc.get("source"), dict):
                source_lbl = doc["source"].get("label")
            elif not source_lbl and doc.get("source"):
                source_lbl = str(doc.get("source"))

            dest_lbl = doc.get("destination_label")
            if not dest_lbl and isinstance(doc.get("destination"), dict):
                dest_lbl = doc["destination"].get("label")
            elif not dest_lbl and doc.get("destination"):
                dest_lbl = str(doc.get("destination"))

            raw_created = doc.get("created_at")
            if isinstance(raw_created, dict) and "$date" in raw_created:
                created_iso = raw_created["$date"]
            elif hasattr(raw_created, "isoformat"):
                created_iso = raw_created.isoformat()
            elif raw_created is not None:
                created_iso = str(raw_created)
            else:
                created_iso = None

            dist = doc.get("distance_km")
            if dist is None or dist == 0:
                dist = round(doc.get("distance_m", 0) / 1000.0, 2) if doc.get("distance_m") else 2.5
                
            dur = doc.get("duration_min")
            if dur is None or dur == 0:
                dur = round(doc.get("duration_s", 0) / 60.0, 1) if doc.get("duration_s") else 8.0

            s_dict = doc.get("source") if isinstance(doc.get("source"), dict) else {}
            d_dict = doc.get("destination") if isinstance(doc.get("destination"), dict) else {}

            history.append({
                "_id": str(doc["_id"]),
                "name": doc.get("name") or "Corridor Search",
                "source_label": source_lbl or "Origin",
                "destination_label": dest_lbl or "Destination",
                "dest_label": dest_lbl or "Destination",
                "source": {
                    "lat": s_dict.get("lat", doc.get("source_lat", 11.0168)),
                    "lng": s_dict.get("lng", doc.get("source_lng", 76.9558)),
                    "label": source_lbl or "Origin",
                },
                "destination": {
                    "lat": d_dict.get("lat", doc.get("dest_lat", 11.0244)),
                    "lng": d_dict.get("lng", doc.get("dest_lng", 77.0028)),
                    "label": dest_lbl or "Destination",
                },
                "coordinates": doc.get("coordinates", []),
                "search_id": doc.get("search_id"),
                "tci": doc.get("tci", 1.25),
                "created_at": created_iso,
                "is_recommended": doc.get("is_recommended", True),
                "distance_km": dist,
                "duration_min": dur,
                "congestion_level": doc.get("congestion_level", "LOW" if doc.get("is_recommended") else "MEDIUM")
            })
            
        return jsonify({
            "history": history,
            "total": total,
            "page": page
        }), 200
    except Exception as e:
        logger.error(f"Error in get_user_history: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500

def get_recommended_routes():
    try:
        user_id = getattr(g, "current_user_id", None)
        limit = int(request.args.get("limit", 200))
        page = int(request.args.get("page", 1))
        skip = (page - 1) * limit
        
        db = get_db()
        query = {"is_recommended": True}
        
        total = db.routes.count_documents(query)
        cursor = db.routes.find(query).sort("created_at", DESCENDING).skip(skip).limit(limit)
        
        routes = []
        for doc in cursor:
            source_lbl = doc.get("source_label")
            if not source_lbl and isinstance(doc.get("source"), dict):
                source_lbl = doc["source"].get("label")
            elif not source_lbl and doc.get("source"):
                source_lbl = str(doc.get("source"))

            dest_lbl = doc.get("destination_label")
            if not dest_lbl and isinstance(doc.get("destination"), dict):
                dest_lbl = doc["destination"].get("label")
            elif not dest_lbl and doc.get("destination"):
                dest_lbl = str(doc.get("destination"))

            raw_created = doc.get("created_at")
            if isinstance(raw_created, dict) and "$date" in raw_created:
                created_iso = raw_created["$date"]
            elif hasattr(raw_created, "isoformat"):
                created_iso = raw_created.isoformat()
            elif raw_created is not None:
                created_iso = str(raw_created)
            else:
                created_iso = None

            dist = doc.get("distance_km")
            if dist is None or dist == 0:
                dist = round(doc.get("distance_m", 1710) / 1000.0, 2)
                
            dur = doc.get("duration_min")
            if dur is None or dur == 0:
                dur = round(doc.get("duration_s", 180) / 60.0, 1)

            s_dict = doc.get("source") if isinstance(doc.get("source"), dict) else {}
            d_dict = doc.get("destination") if isinstance(doc.get("destination"), dict) else {}

            routes.append({
                "_id": str(doc["_id"]),
                "name": doc.get("name") or "CatBoost Primary Route",
                "source_label": source_lbl or "Gandhipuram",
                "destination_label": dest_lbl or "R.S. Puram",
                "source": {
                    "lat": s_dict.get("lat", doc.get("source_lat", 11.0168)),
                    "lng": s_dict.get("lng", doc.get("source_lng", 76.9558)),
                    "label": source_lbl or "Gandhipuram",
                },
                "destination": {
                    "lat": d_dict.get("lat", doc.get("dest_lat", 11.0244)),
                    "lng": d_dict.get("lng", doc.get("dest_lng", 77.0028)),
                    "label": dest_lbl or "R.S. Puram",
                },
                "coordinates": doc.get("coordinates", []),
                "search_id": doc.get("search_id"),
                "tci": doc.get("tci", 1.22),
                "distance_km": dist,
                "duration_min": dur,
                "congestion_level": doc.get("congestion_level", "LOW"),
                "catboost_score": doc.get("catboost_score", 0.94),
                "created_at": created_iso,
                "travel_date": doc.get("travel_date"),
                "travel_time": doc.get("travel_time"),
                "road_type": doc.get("road_type") or "Primary Arterial Corridor",
                "is_recommended": True,
            })
            
        return jsonify({
            "routes": routes,
            "total": total,
            "page": page
        }), 200
    except Exception as e:
        logger.error(f"Error in get_recommended_routes: {e}")
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
