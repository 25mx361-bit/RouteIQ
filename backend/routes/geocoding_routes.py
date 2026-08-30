"""
backend/routes/geocoding_routes.py — Geocoding API Endpoints.

Endpoints:
  GET  /api/geocode?q=...       — Geocode search query (returns latitude, longitude, display_name)
  GET  /api/geocode/search?q=   — Autocomplete suggestions (returns list of results)
  POST /api/geocode             — Geocode via JSON body { "query": "..." }
"""
from __future__ import annotations

from flask import Blueprint, request, jsonify
from loguru import logger
from backend.services.geocoding_service import GeocodingService, COIMBATORE_PRESETS

geocoding_routes_bp = Blueprint("geocoding_routes", __name__)
geocoding_service = GeocodingService()


@geocoding_routes_bp.get("/geocode/search")
def geocode_search():
    """
    Autocomplete suggestions for a partial location query.
    Returns a list of matching locations (up to 6), combining local presets + Nominatim.
    """
    query = request.args.get("q", "").strip()
    if not query or len(query) < 2:
        return jsonify([]), 200

    results = []
    q_lower = query.lower()

    # 1. Collect all preset matches first (instant, no HTTP call)
    for key, landmark in COIMBATORE_PRESETS.items():
        if q_lower in key or key in q_lower or any(w in key for w in q_lower.split() if len(w) > 2):
            results.append({
                "latitude": landmark["latitude"],
                "longitude": landmark["longitude"],
                "display_name": landmark["display_name"],
                "source": "preset",
            })
            if len(results) >= 3:
                break

    # 2. Fetch from Nominatim to supplement
    try:
        import requests as req_lib
        params = {
            "q": f"{query}, Coimbatore, Tamil Nadu, India",
            "format": "json",
            "addressdetails": 1,
            "limit": 5,
            "viewbox": "76.7,11.2,77.2,10.8",
            "bounded": 0,
        }
        resp = req_lib.get(
            "https://nominatim.openstreetmap.org/search",
            params=params,
            headers={"User-Agent": "RouteIQ-MCA-Project/1.0", "Accept-Language": "en"},
            timeout=4,
        )
        if resp.status_code == 200:
            for item in resp.json():
                display = item.get("display_name", "")
                lat = float(item["lat"])
                lon = float(item["lon"])
                # Avoid duplicating nearby presets
                is_dup = any(
                    abs(r["latitude"] - lat) < 0.002 and abs(r["longitude"] - lon) < 0.002
                    for r in results
                )
                if not is_dup:
                    results.append({
                        "latitude": lat,
                        "longitude": lon,
                        "display_name": display,
                        "source": "nominatim",
                    })
    except Exception as e:
        logger.warning(f"Nominatim search error for '{query}': {e}")

    return jsonify(results[:6]), 200


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
