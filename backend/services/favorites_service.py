"""
backend/services/favorites_service.py
"""
from typing import List, Dict, Any, Optional
from pymongo import DESCENDING
from backend.database import get_db
from backend.models.favorites import Favorite

def get_user_favorites(user_id: str, db=None) -> List[Dict[str, Any]]:
    db_conn = db if db is not None else get_db()
    from bson import ObjectId
    ids = [str(user_id)]
    if ObjectId.is_valid(str(user_id)):
        ids.append(ObjectId(str(user_id)))
    docs = Favorite.find_many(
        db_conn,
        {"user_id": {"$in": ids}},
        sort=[("created_at", DESCENDING)]
    )
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return docs

def add_favorite(user_id: str, data: Dict[str, Any], db=None) -> str:
    db_conn = db if db is not None else get_db()
    
    favorite_data = {
        "user_id": str(user_id),
        "source": data.get("source"),
        "destination": data.get("destination"),
        "route_name": data.get("route_name"),
        "distance_km": data.get("distance_km"),
        "duration_min": data.get("duration_min"),
        "congestion_level": data.get("congestion_level"),
    }
    if "catboost_score" in data:
        favorite_data["catboost_score"] = data["catboost_score"]
        
    result = Favorite.insert(db_conn, favorite_data)
    return str(result.inserted_id)

def remove_favorite(favorite_id: str, user_id: str, db=None) -> bool:
    db_conn = db if db is not None else get_db()
    doc = Favorite.find_by_id(db_conn, favorite_id)
    if not doc:
        return False
    if str(doc.get("user_id")) != str(user_id):
        return False
    result = Favorite.delete(db_conn, favorite_id)
    return result.deleted_count > 0
