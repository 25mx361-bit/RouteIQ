"""
backend/routes/landslide_routes.py — Landslide Alert & Hazard Blueprints.

Endpoints:
  GET    /api/landslides              — List all landslides
  POST   /api/landslides              — Create landslide alert (Admin only)
  PUT    /api/landslides/<id>         — Update landslide details (Admin only)
  DELETE /api/landslides/<id>         — Delete landslide alert (Admin only)
  PUT    /api/landslides/<id>/activate — Mark as ACTIVE & enforce blockade (Admin only)
  PUT    /api/landslides/<id>/resolve — Mark as RESOLVED & lift blockade (Admin only)
  POST   /api/landslides/check-route  — Check if route polyline collides with active hazard
"""
from __future__ import annotations

from flask import Blueprint
from backend.controllers.landslide_controller import (
    list_landslides_controller,
    create_landslide_controller,
    update_landslide_controller,
    delete_landslide_controller,
    activate_landslide_controller,
    resolve_landslide_controller,
    check_route_impact_controller,
)

landslide_routes_bp = Blueprint("landslide_routes", __name__)

landslide_routes_bp.get("")(list_landslides_controller)
landslide_routes_bp.get("/")(list_events := list_landslides_controller)
landslide_routes_bp.post("")(create_landslide_controller)
landslide_routes_bp.post("/")(create_landslide_controller)
landslide_routes_bp.put("/<landslide_id>")(update_landslide_controller)
landslide_routes_bp.delete("/<landslide_id>")(delete_landslide_controller)
landslide_routes_bp.put("/<landslide_id>/activate")(activate_landslide_controller)
landslide_routes_bp.put("/<landslide_id>/resolve")(resolve_landslide_controller)
landslide_routes_bp.post("/check-route")(check_route_impact_controller)
