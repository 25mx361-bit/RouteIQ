"""
routes/prediction.py — Traffic Prediction Blueprint
=====================================================
Endpoints:
  POST /api/v1/prediction/predict  — Run PatchTST + CatBoost pipeline
  GET  /api/v1/prediction/history  — Fetch past prediction results for the user
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from loguru import logger

prediction_bp = Blueprint("prediction", __name__)


# ---------------------------------------------------------------------------
# POST /api/v1/prediction/predict
# ---------------------------------------------------------------------------
@prediction_bp.post("/predict")
@jwt_required()
def predict():
    """
    Accept a travel request and return predicted congestion + recommended route.

    Expected JSON body:
    {
        "source":       { "lat": float, "lng": float, "label": str },
        "destination":  { "lat": float, "lng": float, "label": str },
        "travel_date":  "YYYY-MM-DD",
        "travel_time":  "HH:MM"
    }

    Returns prediction results from PatchTST + CatBoost pipeline.
    NOTE: ML inference is wired up in Phase 3 (model training & integration).
          This endpoint currently validates input and returns a 501 stub.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "invalid_json", "message": "Request body must be JSON."}), 400

    required = ["source", "destination", "travel_date", "travel_time"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": "missing_fields", "message": f"Missing fields: {missing}"}), 422

    logger.info(f"Prediction requested: {data.get('source')} -> {data.get('destination')} @ {data.get('travel_date')} {data.get('travel_time')}")

    # TODO (Phase 3): Call PatchTST inference then CatBoost recommendation.
    return jsonify({
        "status": "not_implemented",
        "message": "ML pipeline will be connected in Phase 3 (model training & integration).",
    }), 501


# ---------------------------------------------------------------------------
# GET /api/v1/prediction/history
# ---------------------------------------------------------------------------
@prediction_bp.get("/history")
@jwt_required()
def history():
    """Return the last 20 prediction results for the authenticated user."""
    user_id = get_jwt_identity()
    from backend.extensions import mongo
    from bson import ObjectId

    records = list(
        mongo.db.predictions
        .find({"user_id": user_id}, {"_id": 1, "created_at": 1, "source": 1, "destination": 1, "recommendation": 1})
        .sort("created_at", -1)
        .limit(20)
    )
    for r in records:
        r["_id"] = str(r["_id"])

    return jsonify({"predictions": records}), 200
