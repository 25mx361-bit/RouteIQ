"""
backend/routes/route_routes.py — Routing & Alternatives Endpoints.

Endpoints:
  GET  /api/routes/search        — Search alternative routes via query params
  POST /api/routes/search        — Search alternative routes via JSON payload
  GET  /api/routes/alternatives  — Fetch saved alternative routes by search_id
"""
from __future__ import annotations

from flask import Blueprint
from backend.middleware.auth_middleware import optional_auth
from backend.controllers.route_controller import search_routes, get_alternatives

route_routes_bp = Blueprint("route_routes", __name__)

# Search alternative routes (with optional auth to capture user_id if logged in)
route_routes_bp.route("/search", methods=["GET", "POST"])(optional_auth(search_routes))

# Retrieve alternatives by search_id
route_routes_bp.get("/alternatives")(get_alternatives)
