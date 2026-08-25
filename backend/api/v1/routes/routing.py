"""
routes/routing.py — Route Generation Blueprint
===============================================
Endpoints:
  POST /api/v1/routing/routes    — Generate available routes via OpenRouteService
  POST /api/v1/routing/geocode   — Geocode a place name to lat/lng
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from loguru import logger

routing_bp = Blueprint("routing", __name__)


# ---------------------------------------------------------------------------
# POST /api/v1/routing/geocode
# ---------------------------------------------------------------------------
@routing_bp.post("/geocode")
def geocode():
    """
    Convert a place name / address into geographical coordinates.

    Expected JSON: { "query": "Chennai, India" }
    Returns:       { "lat": float, "lng": float, "label": str }

    NOTE: OpenRouteService geocoding will be wired in Phase 2.
    """
    data = request.get_json(silent=True)
    if not data or "query" not in data:
        return jsonify({"error": "missing_fields", "message": "'query' is required."}), 422

    query = data["query"].strip()
    if not query:
        return jsonify({"error": "invalid_input", "message": "Query must not be empty."}), 422

    logger.debug(f"Geocode request: {query}")

    # TODO (Phase 2): Call OpenRouteService Geocoding API.
    return jsonify({
        "status": "not_implemented",
        "message": "Geocoding via OpenRouteService will be connected in Phase 2.",
        "query": query,
    }), 501


# ---------------------------------------------------------------------------
# POST /api/v1/routing/routes
# ---------------------------------------------------------------------------
@routing_bp.post("/routes")
@jwt_required()
def get_routes():
    """
    Generate available routes between source and destination.

    Expected JSON:
    {
        "source":      { "lat": float, "lng": float },
        "destination": { "lat": float, "lng": float },
        "profile":     "driving-car"  // optional, default: driving-car
    }

    Returns list of routes with distance, duration, and geometry.
    NOTE: Full ORS integration in Phase 2.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "invalid_json", "message": "Request body must be JSON."}), 400

    if "source" not in data or "destination" not in data:
        return jsonify({"error": "missing_fields", "message": "'source' and 'destination' are required."}), 422

    logger.debug(f"Route generation: {data['source']} -> {data['destination']}")

    # TODO (Phase 2): Call OpenRouteService Directions API, return routes with geometry.
    return jsonify({
        "status": "not_implemented",
        "message": "Route generation via OpenRouteService will be connected in Phase 2.",
    }), 501
