"""
routes/traffic.py — Traffic Data Blueprint
==========================================
Endpoints:
  GET  /api/v1/traffic/current      — Fetch current traffic snapshot (TomTom)
  GET  /api/v1/traffic/historical   — Query historical traffic records from DB
  POST /api/v1/traffic/collect      — Trigger manual data collection job
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

traffic_bp = Blueprint("traffic", __name__)


# ---------------------------------------------------------------------------
# GET /api/v1/traffic/current
# ---------------------------------------------------------------------------
@traffic_bp.get("/current")
@jwt_required()
def current_traffic():
    """
    Return current traffic flow data for given coordinates.

    Query params: lat, lng, zoom (optional, default=10)
    NOTE: TomTom Traffic Flow API integration in Phase 2.
    """
    lat  = request.args.get("lat", type=float)
    lng  = request.args.get("lng", type=float)

    if lat is None or lng is None:
        return jsonify({"error": "missing_params", "message": "'lat' and 'lng' query parameters are required."}), 422

    logger.debug(f"Current traffic requested at ({lat}, {lng})")

    # TODO (Phase 2): Call TomTom Traffic Flow API.
    return jsonify({
        "status": "not_implemented",
        "message": "TomTom Traffic Flow integration will be connected in Phase 2.",
        "coordinates": {"lat": lat, "lng": lng},
    }), 501


# ---------------------------------------------------------------------------
# GET /api/v1/traffic/historical
# ---------------------------------------------------------------------------
@traffic_bp.get("/historical")
@jwt_required()
def historical_traffic():
    """
    Query historical traffic records stored in MongoDB.

    Query params:
        segment_id  — Road segment identifier
        start_date  — ISO date string (YYYY-MM-DD)
        end_date    — ISO date string (YYYY-MM-DD)
        limit       — Max records (default 500)
    """
    segment_id = request.args.get("segment_id")
    start_date = request.args.get("start_date")
    end_date   = request.args.get("end_date")
    limit      = request.args.get("limit", 500, type=int)

    from backend.extensions import mongo

    query: dict = {}
    if segment_id:
        query["segment_id"] = segment_id
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            query["timestamp"]["$gte"] = start_date
        if end_date:
            query["timestamp"]["$lte"] = end_date

    records = list(
        mongo.db.traffic_data
        .find(query, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )

    return jsonify({"count": len(records), "records": records}), 200


# ---------------------------------------------------------------------------
# POST /api/v1/traffic/collect
# ---------------------------------------------------------------------------
@traffic_bp.post("/collect")
@jwt_required()
def trigger_collection():
    """
    Manually trigger a traffic data collection job.
    Normally this runs on a schedule via APScheduler.
    NOTE: Scheduler jobs defined in Phase 2.
    """
    logger.info("Manual traffic data collection triggered via API.")
    # TODO (Phase 2): Enqueue APScheduler job for TomTom data collection.
    return jsonify({
        "status": "not_implemented",
        "message": "Scheduled data collection will be set up in Phase 2.",
    }), 501
