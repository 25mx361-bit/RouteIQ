"""
backend/routes/user_routes.py
"""
from flask import Blueprint
from backend.middleware.auth_middleware import require_auth
from backend.controllers.user_controller import get_user_stats, get_user_history

user_routes_bp = Blueprint("user_routes", __name__)

user_routes_bp.get("/stats")(require_auth(get_user_stats))
user_routes_bp.get("/history")(require_auth(get_user_history))
