"""
backend/routes/event_routes.py — Public Events, Festivals & Marriages API Blueprints.

Endpoints:
  GET    /api/events              — List / query active events (filters: type, status, date, lat, lng)
  POST   /api/events              — Create new event (Admin only)
  PUT    /api/events/<event_id>   — Update event (Admin only)
  DELETE /api/events/<event_id>   — Delete event (Admin only)
  POST   /api/events/route-impact — Calculate cumulative bottleneck score on route coordinates
"""
from __future__ import annotations

from flask import Blueprint
from backend.controllers.event_controller import (
    list_events_controller,
    create_event_controller,
    update_event_controller,
    delete_event_controller,
    evaluate_route_impact_controller,
)

event_routes_bp = Blueprint("event_routes", __name__)

event_routes_bp.get("")(list_events_controller)
event_routes_bp.get("/")(list_events_controller)
event_routes_bp.post("")(create_event_controller)
event_routes_bp.post("/")(create_event_controller)
event_routes_bp.put("/<event_id>")(update_event_controller)
event_routes_bp.delete("/<event_id>")(delete_event_controller)
event_routes_bp.post("/route-impact")(evaluate_route_impact_controller)
