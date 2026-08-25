"""
backend/controllers/traffic_controller.py — Traffic Flow API Controller.

Handles HTTP validation and invokes TrafficService for point & route traffic queries.
"""
from __future__ import annotations

from flask import request, jsonify
from loguru import logger
from backend.services.traffic_service import TrafficService

traffic_service = TrafficService()


def get_current_traffic():
    """
    Handle GET /api/traffic/current?lat=...&lng=...&zoom=10
    """
    try:
        lat = float(request.args.get("lat", ""))
        lng = float(request.args.get("lng", ""))
        zoom = int(request.args.get("zoom", 10))
    except (ValueError, TypeError):
        return jsonify({
            "error": "validation_error",
            "message": "'lat' and 'lng' query parameters must be valid numbers.",
        }), 422

    if not (-90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0):
        return jsonify({
            "error": "validation_error",
            "message": "Latitude or Longitude out of valid geographic range.",
        }), 422

    try:
        data = traffic_service.get_flow_at_point(lat=lat, lng=lng, zoom=zoom)
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Traffic query failed for ({lat}, {lng}): {e}")
        return jsonify({
            "error": "internal_error",
            "message": "Failed to fetch traffic flow data.",
        }), 500


def get_route_traffic():
    """
    Handle POST /api/traffic/route-flow
    JSON payload: { "coordinates": [[lat1, lng1], [lat2, lng2], ...] }
    """
    body = request.get_json(silent=True) or {}
    coordinates = body.get("coordinates", [])

    if not isinstance(coordinates, list) or len(coordinates) == 0:
        return jsonify({
            "error": "bad_request",
            "message": "Field 'coordinates' must be a non-empty list of [lat, lng] points.",
        }), 400

    try:
        flow_data = traffic_service.get_route_traffic_flow(coordinates)
        return jsonify(flow_data), 200
    except Exception as e:
        logger.error(f"Route traffic query failed: {e}")
        return jsonify({
            "error": "internal_error",
            "message": "Failed to analyze route traffic flow.",
        }), 500
