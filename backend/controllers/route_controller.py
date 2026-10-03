"""
backend/controllers/route_controller.py — Route Generation & Alternatives Controller.

Handles HTTP request validation, invokes RoutingService, and formats clean JSON responses.
"""
from __future__ import annotations

from flask import request, jsonify, g
from loguru import logger

from backend.services.routing_service import (
    RoutingService,
    RoutingError,
    InvalidCoordinatesError,
    RouteNotFoundError,
)

routing_service = RoutingService()


def search_routes():
    """
    Handle GET & POST /api/routes/search
    Query params or JSON payload:
      source_lat, source_lng, dest_lat, dest_lng, source_label, dest_label, date, time
    """
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
    else:
        data = request.args.to_dict()

    try:
        source_lat = float(data.get("source_lat", 0.0))
        source_lng = float(data.get("source_lng", 0.0))
        dest_lat = float(data.get("dest_lat", 0.0))
        dest_lng = float(data.get("dest_lng", 0.0))
    except (ValueError, TypeError):
        return jsonify({
            "error": "validation_error",
            "message": "source_lat, source_lng, dest_lat, and dest_lng must be valid floating point numbers.",
        }), 422

    source_label = data.get("source_label", "")
    dest_label = data.get("dest_label", "")
    travel_date = data.get("date", "")
    travel_time = data.get("time", "")
    vehicle_type = str(data.get("vehicle_type", "car")).lower().strip()
    user_id = getattr(g, "current_user_id", None)

    try:
        result = routing_service.generate_routes(
            source_lat=source_lat,
            source_lng=source_lng,
            dest_lat=dest_lat,
            dest_lng=dest_lng,
            source_label=source_label,
            dest_label=dest_label,
            travel_date=travel_date,
            travel_time=travel_time,
            user_id=user_id,
            vehicle_type=vehicle_type,
        )
        return jsonify(result), 200

    except InvalidCoordinatesError as e:
        return jsonify({"error": "invalid_coordinates", "message": e.message}), e.status_code
    except RouteNotFoundError as e:
        return jsonify({"error": "route_not_found", "message": e.message}), e.status_code
    except RoutingError as e:
        return jsonify({"error": "routing_error", "message": e.message}), e.status_code
    except Exception as e:
        logger.error(f"Unexpected routing error: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to generate routes. Please try again."}), 500


def get_alternatives():
    """Handle GET /api/routes/alternatives?search_id=..."""
    search_id = request.args.get("search_id", "").strip()
    if not search_id:
        return jsonify({
            "error": "bad_request",
            "message": "Query parameter 'search_id' is required.",
        }), 400

    try:
        routes = routing_service.get_routes_by_search_id(search_id)
        return jsonify({
            "search_id": search_id,
            "routes_count": len(routes),
            "routes": routes,
        }), 200
    except RouteNotFoundError as e:
        return jsonify({"error": "not_found", "message": e.message}), 404
    except Exception as e:
        logger.error(f"Unexpected error fetching alternatives: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to fetch alternative routes."}), 500
