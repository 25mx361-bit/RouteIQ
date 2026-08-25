"""
backend/routes/geocoding_routes.py — Geocoding API Endpoints.

Endpoints:
  GET  /api/geocode?q=...    — Geocode search query (returns latitude, longitude, display_name)
  POST /api/geocode          — Geocode via JSON body { "query": "..." }
"""
from __future__ import annotations

from flask import Blueprint, request, jsonify
from loguru import logger
from backend.services.geocoding_service import GeocodingService

geocoding_routes_bp = Blueprint("geocoding_routes", __name__)
geocoding_service = GeocodingService()


@geocoding_routes_bp.get("/geocode")
def geocode_get():
    """Geocode place name passed as query parameter `q`."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({
            "error": "bad_request",
            "message": "Query parameter 'q' is required (e.g. /api/geocode?q=Gandhipuram).",
        }), 400

    try:
        result = geocoding_service.geocode(query)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({
            "error": "not_found",
            "message": str(e),
        }), 404
    except Exception as e:
        logger.error(f"Geocoding error for '{query}': {e}")
        return jsonify({
            "error": "geocoding_failed",
            "message": "Unable to geocode location at this time. Please try again.",
        }), 500


@geocoding_routes_bp.post("/geocode")
def geocode_post():
    """Geocode place name passed in JSON body."""
    data = request.get_json(silent=True) or {}
    query = data.get("query", "") or data.get("q", "")
    query = str(query).strip()

    if not query:
        return jsonify({
            "error": "bad_request",
            "message": "Field 'query' or 'q' is required in JSON body.",
        }), 400

    try:
        result = geocoding_service.geocode(query)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({
            "error": "not_found",
            "message": str(e),
        }), 404
    except Exception as e:
        logger.error(f"Geocoding error for '{query}': {e}")
        return jsonify({
            "error": "geocoding_failed",
            "message": "Unable to geocode location at this time. Please try again.",
        }), 500
