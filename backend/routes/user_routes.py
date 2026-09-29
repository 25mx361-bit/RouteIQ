"""
backend/routes/user_routes.py
"""
from flask import Blueprint
from backend.middleware.auth_middleware import optional_auth
from backend.controllers.user_controller import get_user_stats, get_user_history, get_recommended_routes

user_routes_bp = Blueprint("user_routes", __name__)

user_routes_bp.get("/stats")(optional_auth(get_user_stats))
user_routes_bp.get("/history")(optional_auth(get_user_history))
user_routes_bp.get("/recommended")(optional_auth(get_recommended_routes))
