"""
backend/models/favorites.py — Favorites model
"""
from backend.models.base import BaseModel

class Favorite(BaseModel):
    COLLECTION = "favorites"
    REQUIRED_FIELDS = [
        "user_id",
        "source",
        "destination",
        "route_name",
        "distance_km",
        "duration_min",
        "congestion_level"
    ]
