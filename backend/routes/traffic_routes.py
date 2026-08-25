"""
backend/routes/traffic_routes.py — Traffic Flow & TomTom Endpoints.

Endpoints:
  GET  /api/traffic/current     — Get current traffic flow for coordinates
  POST /api/traffic/route-flow  — Analyze traffic flow across route coordinates
"""
from __future__ import annotations

from flask import Blueprint
from backend.controllers.traffic_controller import get_current_traffic, get_route_traffic

traffic_routes_bp = Blueprint("traffic_routes", __name__)

traffic_routes_bp.get("/current")(get_current_traffic)
traffic_routes_bp.post("/route-flow")(get_route_traffic)
