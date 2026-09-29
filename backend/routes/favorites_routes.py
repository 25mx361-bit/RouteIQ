"""
backend/routes/favorites_routes.py
"""
from flask import Blueprint
from backend.middleware.auth_middleware import optional_auth
from backend.controllers.favorites_controller import list_favorites, create_favorite, delete_favorite

favorites_routes_bp = Blueprint("favorites_routes", __name__)

favorites_routes_bp.add_url_rule("", view_func=optional_auth(list_favorites), methods=["GET"], strict_slashes=False)
favorites_routes_bp.add_url_rule("", view_func=optional_auth(create_favorite), methods=["POST"], strict_slashes=False)
favorites_routes_bp.add_url_rule("/<favorite_id>", view_func=optional_auth(delete_favorite), methods=["DELETE"], strict_slashes=False)

