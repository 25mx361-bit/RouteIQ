"""
routes/prediction.py — Traffic Prediction Blueprint
=====================================================
Endpoints:
  POST /api/v1/prediction/predict  — Run PatchTST + CatBoost pipeline
  GET  /api/v1/prediction/history  — Fetch past prediction results
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from loguru import logger
from datetime import datetime, timezone

prediction_bp = Blueprint("prediction", __name__)


@prediction_bp.post("/predict")
@jwt_required()
def predict():
    """
    Run PatchTST + CatBoost prediction pipeline.

    Expected JSON body:
    {
        "source":       { "lat": float, "lng": float, "label": str },
        "destination":  { "lat": float, "lng": float, "label": str },
        "travel_date":  "YYYY-MM-DD",
        "travel_time":  "HH:MM"
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "invalid_json", "message": "Request body must be JSON."}), 400

    required = ["source", "destination", "travel_date", "travel_time"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": "missing_fields", "message": f"Missing fields: {missing}"}), 422

    user_id = get_jwt_identity()
    logger.info(f"Prediction requested by user={user_id}: {data.get('source')} -> {data.get('destination')} @ {data.get('travel_date')} {data.get('travel_time')}")

    try:
        from backend.database import get_db
        from ml.patchtst.inference import PatchTSTPredictor
        import pandas as pd
        import re

        db = get_db()

        # Parse target datetime
        travel_date = data["travel_date"]
        travel_time = data["travel_time"]
        try:
            target_dt = datetime.strptime(f"{travel_date} {travel_time}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        except ValueError:
            return jsonify({"error": "invalid_date", "message": "travel_date must be YYYY-MM-DD, travel_time must be HH:MM"}), 422

        source = data["source"]
        dest = data["destination"]
        src_lat = source.get("lat", 11.0168)
        src_lng = source.get("lng", 76.9558)

        # Load recent traffic data for context
        recent_traffic = list(
            db.traffic_data
            .find({"timestamp": {"$lte": datetime.now(timezone.utc)}})
            .sort("timestamp", -1)
            .limit(200)
        )
        recent_df = pd.DataFrame(recent_traffic) if recent_traffic else pd.DataFrame()

        # Get PatchTST prediction
        predictor = PatchTSTPredictor.get_instance()

        # Approximate route distance from lat/lng
        import math
        dest_lat = dest.get("lat", src_lat)
        dest_lng = dest.get("lng", src_lng)
        lat_diff = abs(src_lat - dest_lat)
        lng_diff = abs(src_lng - dest_lng)
        approx_dist_km = math.sqrt(lat_diff**2 + lng_diff**2) * 111.0  # rough km per degree
        approx_dist_km = max(0.5, approx_dist_km)

        prediction = predictor.predict_route_traffic(
            distance_km=approx_dist_km,
            target_datetime=target_dt,
            precipitation=0.0,
            recent_db_data=recent_df if len(recent_df) > 0 else None,
        )

        # Calculate TCI
        pred_tt = prediction.get("predicted_travel_time", 600.0)
        ff_tt = prediction.get("free_flow_travel_time", pred_tt * 0.7)
        tci = round(pred_tt / max(ff_tt, 1.0), 4)

        # Store prediction in DB
        pred_record = {
            "user_id": user_id,
            "source_label": source.get("label", f"{src_lat},{src_lng}"),
            "destination_label": dest.get("label", f"{dest_lat},{dest_lng}"),
            "source_lat": src_lat,
            "source_lng": src_lng,
            "dest_lat": dest_lat,
            "dest_lng": dest_lng,
            "travel_date": travel_date,
            "travel_time": travel_time,
            "target_datetime": target_dt,
            "predicted_speed_kmh": prediction.get("predicted_speed_kmh"),
            "predicted_travel_time": pred_tt,
            "predicted_tci": tci,
            "congestion_level": prediction.get("congestion_level", "MEDIUM"),
            "model_version": prediction.get("model_version", "unknown"),
            "prediction_method": prediction.get("method", "unknown"),
            "distance_km": round(approx_dist_km, 2),
            "created_at": datetime.now(timezone.utc),
        }
        db.predictions.insert_one(pred_record)

        return jsonify({
            "status": "success",
            "prediction": {
                "predicted_speed_kmh": prediction.get("predicted_speed_kmh"),
                "predicted_travel_time_min": prediction.get("predicted_travel_time_min"),
                "predicted_travel_time_sec": pred_tt,
                "predicted_tci": tci,
                "congestion_level": prediction.get("congestion_level"),
                "free_flow_speed_kmh": prediction.get("free_flow_speed_kmh"),
                "free_flow_travel_time_min": prediction.get("free_flow_travel_time_min"),
                "delay_minutes": prediction.get("delay_minutes", 0),
                "model_version": prediction.get("model_version"),
                "method": prediction.get("method"),
            },
            "route_info": {
                "source": source,
                "destination": dest,
                "target_datetime": target_dt.isoformat(),
                "distance_km": round(approx_dist_km, 2),
            },
        }), 200

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"error": "prediction_failed", "message": str(e)}), 500


@prediction_bp.get("/history")
@jwt_required()
def history():
    """Return the last 20 prediction results for the authenticated user."""
    user_id = get_jwt_identity()
    from backend.database import get_db

    db = get_db()
    records = list(
        db.predictions
        .find({"user_id": user_id}, {"_id": 1, "created_at": 1, "source_label": 1,
                                     "destination_label": 1, "predicted_tci": 1,
                                     "congestion_level": 1, "model_version": 1})
        .sort("created_at", -1)
        .limit(20)
    )
    for r in records:
        r["_id"] = str(r["_id"])
        if "created_at" in r and hasattr(r["created_at"], "isoformat"):
            r["created_at"] = r["created_at"].isoformat()

    return jsonify({"predictions": records}), 200
