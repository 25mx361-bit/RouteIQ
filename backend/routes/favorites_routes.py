"""
backend/routes/favorites_routes.py
"""
from flask import Blueprint
from backend.middleware.auth_middleware import require_auth
from backend.controllers.favorites_controller import list_favorites, create_favorite, delete_favorite

favorites_routes_bp = Blueprint("favorites_routes", __name__)

favorites_routes_bp.get("/")(require_auth(list_favorites))
favorites_routes_bp.post("/")(require_auth(create_favorite))
favorites_routes_bp.delete("/<favorite_id>")(require_auth(delete_favorite))
