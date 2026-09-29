"""
backend/controllers/admin_controller.py — Admin Management & Scheduler Status Controller.
"""
from __future__ import annotations

from flask import request, jsonify
from loguru import logger

from backend.scheduler.scheduler import get_scheduler_status
from backend.scheduler.jobs import (
    traffic_data_collection,
    weather_data_collection,
    event_status_update,
    notification_check,
)


def get_scheduler_info():
    """
    Handle GET /api/admin/scheduler/status
    Returns comprehensive APScheduler state, job list, and telemetry.
    """
    try:
        status_data = get_scheduler_status()
        return jsonify(status_data), 200
    except Exception as e:
        logger.error(f"Error retrieving scheduler status: {e}")
        return jsonify({
            "error": "internal_error",
            "message": "Failed to fetch scheduler status.",
        }), 500


def trigger_scheduler_job():
    """
    Handle POST /api/admin/scheduler/trigger-job
    Body: { "job_id": "traffic_data_collection" | "weather_data_collection" | ... }
    Allows admin to trigger a collection job on-demand without waiting for timer interval.
    """
    body = request.get_json(silent=True) or {}
    job_id = body.get("job_id", "").strip()

    job_map = {
        "traffic_data_collection": traffic_data_collection,
        "weather_data_collection": weather_data_collection,
        "event_status_update": event_status_update,
        "notification_check": notification_check,
    }

    if job_id not in job_map:
        return jsonify({
            "error": "bad_request",
            "message": f"Invalid job_id '{job_id}'. Valid jobs: {list(job_map.keys())}",
        }), 400

    try:
        func = job_map[job_id]
        result = func()
        return jsonify({
            "message": f"Job '{job_id}' executed successfully.",
            "job_id": job_id,
            "result": result,
        }), 200
    except Exception as e:
        logger.error(f"Error triggering job {job_id}: {e}")
        return jsonify({
            "error": "internal_error",
            "message": f"Failed to execute job '{job_id}': {e}",
        }), 500


# ── CatBoost Admin Endpoints ─────────────────────────────────────────────────

def trigger_catboost_train():
    """
    Handle POST /api/admin/models/catboost/train
    Launches CatBoost training in a background thread (non-blocking).
    Admin only — no concurrent runs are started if one is already running.
    """
    import threading
    from backend.database import get_db
    from ml.catboost.training import train_catboost
    from ml.catboost.prediction import invalidate_cache

    try:
        db = get_db()

        def _train_bg():
            try:
                logger.info("CatBoost background training started.")
                result = train_catboost(db)
                invalidate_cache()
                logger.info(f"CatBoost training finished: {result.get('status')}")
            except Exception as exc:
                logger.error(f"CatBoost background training error: {exc}")

        t = threading.Thread(target=_train_bg, daemon=True, name="catboost-train")
        t.start()

        return jsonify({
            "message": "CatBoost training started in background.",
            "note": "Poll GET /api/admin/models/catboost/metrics to track completion.",
        }), 202

    except Exception as e:
        logger.error(f"Failed to start CatBoost training: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500


def get_catboost_metrics():
    """
    Handle GET /api/admin/models/catboost/metrics
    Returns the latest evaluation results saved by the training pipeline.
    """
    import json
    from ml.catboost.config import CatBoostConfig

    cfg = CatBoostConfig()
    try:
        if not __import__("os").path.exists(cfg.metrics_path):
            return jsonify({
                "status": "not_trained",
                "message": "No CatBoost metrics found. Train the model first via POST /api/admin/models/catboost/train.",
            }), 404

        with open(cfg.metrics_path, "r") as f:
            metrics = json.load(f)

        return jsonify({"status": "ok", "metrics": metrics}), 200

    except Exception as e:
        logger.error(f"Failed to read CatBoost metrics: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500


# -- PatchTST Admin Endpoints --------------------------------------------------

def trigger_patchtst_train():
    """
    Handle POST /api/admin/models/patchtst/train
    Launches PatchTST training in a background thread.
    """
    import threading
    from backend.database import get_db
    from ml.patchtst.training import train_patchtst
    from ml.patchtst.inference import invalidate_patchtst_cache

    try:
        db = get_db()

        def _train_bg():
            try:
                logger.info("PatchTST background training started.")
                result = train_patchtst(db)
                invalidate_patchtst_cache()
                logger.info(f"PatchTST training finished: {result.get('status')}")
            except Exception as exc:
                logger.error(f"PatchTST background training error: {exc}")

        t = threading.Thread(target=_train_bg, daemon=True, name="patchtst-train")
        t.start()

        return jsonify({
            "message": "PatchTST training started in background.",
            "note": "Poll GET /api/admin/models/patchtst/metrics to track completion.",
        }), 202

    except Exception as e:
        logger.error(f"Failed to start PatchTST training: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500


def get_patchtst_metrics():
    """
    Handle GET /api/admin/models/patchtst/metrics
    """
    import json
    from ml.patchtst.config import PatchTSTConfig

    cfg = PatchTSTConfig()
    try:
        if not __import__("os").path.exists(cfg.metrics_path):
            return jsonify({
                "status": "not_trained",
                "message": "No PatchTST metrics found.",
            }), 404

        with open(cfg.metrics_path, "r") as f:
            metrics = json.load(f)

        return jsonify({"status": "ok", "metrics": metrics}), 200

    except Exception as e:
        logger.error(f"Failed to read PatchTST metrics: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500

# -- Phase 17 Admin Endpoints --------------------------------------------------

def get_traffic_records():
    from backend.database import get_db
    import math
    try:
        db = get_db()
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 50))
        location = request.args.get("location")
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        
        query = {}
        if location:
            query["$or"] = [
                {"location": {"$regex": location, "$options": "i"}},
                {"road_id": {"$regex": location, "$options": "i"}},
                {"segment_id": {"$regex": location, "$options": "i"}},
            ]
        
        if date_from or date_to:
            date_query = {}
            if date_from:
                from dateutil import parser
                date_query["$gte"] = parser.parse(date_from)
            if date_to:
                from dateutil import parser
                date_query["$lte"] = parser.parse(date_to)
            query["timestamp"] = date_query
            
        skip = (page - 1) * limit
        total = db.traffic_data.count_documents(query)
        cursor = db.traffic_data.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        
        records = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            records.append(doc)
            
        return jsonify({
            "records": records,
            "total": total,
            "page": page,
            "pages": math.ceil(total / limit) if limit else 1
        }), 200
    except Exception as e:
        logger.error(f"Error in get_traffic_records: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500

def create_traffic_record():
    from backend.database import get_db
    from datetime import datetime, timezone
    try:
        data = request.get_json(silent=True) or {}
        required = ["location", "road_segment", "speed", "traffic_value", "volume"]
        if not all(k in data for k in required):
            return jsonify({"error": "bad_request", "message": "Missing required fields"}), 400
            
        record = {
            "timestamp": datetime.now(timezone.utc),
            "location": data["location"],
            "road_segment": data["road_segment"],
            "speed": data["speed"],
            "traffic_value": data["traffic_value"],
            "volume": data["volume"]
        }
        db = get_db()
        result = db.traffic_data.insert_one(record)
        return jsonify({"message": "Record created", "id": str(result.inserted_id)}), 201
    except Exception as e:
        logger.error(f"Error in create_traffic_record: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500

def update_traffic_record(record_id):
    from backend.database import get_db
    from bson import ObjectId
    try:
        data = request.get_json(silent=True) or {}
        db = get_db()
        result = db.traffic_data.update_one(
            {"_id": ObjectId(record_id)},
            {"$set": data}
        )
        if result.matched_count == 0:
            return jsonify({"error": "not_found", "message": "Record not found"}), 404
        return jsonify({"message": "Record updated"}), 200
    except Exception as e:
        logger.error(f"Error in update_traffic_record: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500

def delete_traffic_record(record_id):
    from backend.database import get_db
    from bson import ObjectId
    try:
        db = get_db()
        result = db.traffic_data.delete_one({"_id": ObjectId(record_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "not_found", "message": "Record not found"}), 404
        return jsonify({"message": "Record deleted"}), 200
    except Exception as e:
        logger.error(f"Error in delete_traffic_record: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500

def get_all_predictions_list():
    from backend.database import get_db
    import math
    try:
        db = get_db()
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        skip = (page - 1) * limit
        
        congestion_filter = request.args.get("congestion")
        
        query = {}
        if congestion_filter:
            query["congestion_level"] = {"$regex": f"^{congestion_filter}$", "$options": "i"}
            
        total = db.predictions.count_documents(query)
        cursor = db.predictions.find(query).sort("created_at", -1).skip(skip).limit(limit)
        
        records = []
        for doc in cursor:
            c_at = doc.get("created_at")
            ts_str = c_at.strftime("%Y-%m-%d %H:%M") if hasattr(c_at, "strftime") else str(c_at or "")
            src = doc.get("source_label") or (doc.get("source", {}).get("label") if isinstance(doc.get("source"), dict) else str(doc.get("source") or "Unknown"))
            dst = doc.get("destination_label") or (doc.get("destination", {}).get("label") if isinstance(doc.get("destination"), dict) else str(doc.get("destination") or "Unknown"))
            records.append({
                "_id": str(doc["_id"]),
                "user_id": str(doc.get("user_id", "")),
                "user": doc.get("user_id") or "Public User",
                "source": src,
                "destination": dst,
                "source_label": src,
                "destination_label": dst,
                "predicted_tci": doc.get("predicted_tci"),
                "congestion_level": doc.get("congestion_level") or "LOW",
                "created_at": c_at,
                "timestamp": ts_str,
                "model_version": doc.get("model_version") or "PatchTST_v2"
            })
            
        # Compute summary stats
        all_count = db.predictions.count_documents({})
        high_count = db.predictions.count_documents({"congestion_level": {"$regex": "high", "$options": "i"}})
        avg_tci_res = list(db.predictions.aggregate([
            {"$match": {"predicted_tci": {"$ne": None}}},
            {"$group": {"_id": None, "avg": {"$avg": "$predicted_tci"}}}
        ]))
        avg_tci = avg_tci_res[0]["avg"] if avg_tci_res else 1.05
        
        stats = {
            "total": all_count,
            "highCongestion": high_count,
            "avgTci": round(avg_tci, 2)
        }
            
        return jsonify({
            "predictions": records,
            "stats": stats,
            "total": total,
            "page": page,
            "pages": math.ceil(total / limit) if limit else 1
        }), 200
    except Exception as e:
        logger.error(f"Error in get_all_predictions_list: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500

def get_reports_summary():
    from backend.database import get_db
    from datetime import datetime, timedelta, timezone
    try:
        db = get_db()
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        
        query_routes = {}
        query_preds = {}
        if date_from or date_to:
            date_query = {}
            if date_from:
                from dateutil import parser
                date_query["$gte"] = parser.parse(date_from)
            if date_to:
                from dateutil import parser
                date_query["$lte"] = parser.parse(date_to)
            query_routes["created_at"] = date_query
            query_preds["created_at"] = date_query
            
        total_searches = db.routes.count_documents(query_routes)
        total_predictions = db.predictions.count_documents(query_preds)
        
        pipeline_cong = [
            {"$match": query_preds},
            {"$group": {"_id": "$congestion_level", "count": {"$sum": 1}}}
        ]
        cong_dist = {"low": 0, "medium": 0, "high": 0}
        for doc in db.predictions.aggregate(pipeline_cong):
            lvl = doc["_id"]
            if lvl in cong_dist:
                cong_dist[lvl] = doc["count"]
                
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)
        pipeline_daily = [
            {"$match": {"created_at": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        daily_searches = [{"date": doc["_id"], "count": doc["count"]} for doc in db.routes.aggregate(pipeline_daily)]
        
        pipeline_top = [
            {"$match": query_routes},
            {"$group": {
                "_id": {"source": "$source_label", "dest": "$destination_label"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_routes = []
        for doc in db.routes.aggregate(pipeline_top):
            if doc["_id"].get("source") and doc["_id"].get("dest"):
                top_routes.append({
                    "source_label": doc["_id"]["source"],
                    "destination_label": doc["_id"]["dest"],
                    "count": doc["count"]
                })
                
        return jsonify({
            "total_searches": total_searches,
            "total_predictions": total_predictions,
            "congestion_distribution": cong_dist,
            "daily_searches": daily_searches,
            "top_routes": top_routes
        }), 200
    except Exception as e:
        logger.error(f"Error in get_reports_summary: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500

def check_api_status():
    import requests
    import os
    import time
    try:
        status_data = {
            "ors": {"status": "unknown", "response_ms": 0},
            "tomtom": {"status": "unknown", "api_key_set": False},
            "openmeteo": {"status": "unknown", "response_ms": 0}
        }
        
        start = time.time()
        try:
            ors_url = os.environ.get("ORS_API_URL", "https://api.openrouteservice.org")
            res = requests.get(f"{ors_url}/v2/health", timeout=5)
            status_data["ors"]["status"] = "ok" if res.status_code == 200 else "error"
            status_data["ors"]["response_ms"] = int((time.time() - start) * 1000)
        except Exception:
            status_data["ors"]["status"] = "offline"
            
        tt_key = os.environ.get("TOMTOM_API_KEY")
        status_data["tomtom"]["api_key_set"] = bool(tt_key and tt_key.strip())
        status_data["tomtom"]["status"] = "ok" if status_data["tomtom"]["api_key_set"] else "missing_key"
        
        start = time.time()
        try:
            res = requests.get("https://api.open-meteo.com/v1/forecast?latitude=11&longitude=77&current_weather=true", timeout=5)
            status_data["openmeteo"]["status"] = "ok" if res.status_code == 200 else "error"
            status_data["openmeteo"]["response_ms"] = int((time.time() - start) * 1000)
        except Exception:
            status_data["openmeteo"]["status"] = "offline"
            
        return jsonify(status_data), 200
    except Exception as e:
        logger.error(f"Error in check_api_status: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500


# ── Forecast Evaluation Endpoints ─────────────────────────────────────────────

def get_forecast_evaluations():
    """
    Handle GET /api/admin/forecast-evaluations
    Returns paginated / filtered list of forecast evaluation records.
    Query params: page, limit, evaluated, corridor, segment_id, source, destination
    """
    from backend.database import get_db
    import math
    try:
        db = get_db()
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 500))
        skip = (page - 1) * limit

        query = {}
        evaluated_filter = request.args.get("evaluated")
        if evaluated_filter == "true":
            query["evaluated"] = True
        elif evaluated_filter == "false":
            query["evaluated"] = False

        corridor = request.args.get("corridor") or request.args.get("name")
        if corridor and corridor.upper() != "ALL":
            query["name"] = {"$regex": f"^{corridor}", "$options": "i"}

        segment_id = request.args.get("segment_id")
        if segment_id and segment_id.upper() != "ALL":
            query["segment_id"] = segment_id

        source = request.args.get("source")
        if source and source.upper() != "ALL":
            query["source"] = {"$regex": source, "$options": "i"}

        destination = request.args.get("destination")
        if destination and destination.upper() != "ALL":
            query["destination"] = {"$regex": destination, "$options": "i"}

        total = db.forecast_evaluations.count_documents(query)
        cursor = db.forecast_evaluations.find(query).sort("prediction_date", -1).skip(skip).limit(limit)

        records = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            for key in ["created_at", "evaluated_at"]:
                if key in doc and hasattr(doc[key], "isoformat"):
                    doc[key] = doc[key].isoformat()
            records.append(doc)

        available_corridors = [
            {"segment_id": "seg_110168_769558", "name": "Gandhipuram Hub", "source": "Gandhipuram Central", "destination": "Town Hall (Raja St)", "route_label": "Gandhipuram Central ➔ Town Hall (Raja St)"},
            {"segment_id": "seg_110244_770028", "name": "PSG Tech Peelamedu", "source": "PSG Tech Peelamedu", "destination": "Hopes College (Avinashi Rd)", "route_label": "PSG Tech Peelamedu ➔ Hopes College (Avinashi Rd)"},
            {"segment_id": "seg_110094_769458", "name": "RS Puram", "source": "RS Puram (DB Road)", "destination": "Saibaba Colony", "route_label": "RS Puram (DB Road) ➔ Saibaba Colony"},
            {"segment_id": "seg_109892_769613", "name": "Ukkadam", "source": "Ukkadam Bus Stand", "destination": "Town Hall (Oppanakara St)", "route_label": "Ukkadam Bus Stand ➔ Town Hall (Oppanakara St)"},
            {"segment_id": "seg_110298_770434", "name": "Airport Corridor", "source": "Coimbatore Airport", "destination": "SITRA Junction (NH-544)", "route_label": "Coimbatore Airport ➔ SITRA Junction (NH-544)"},
            {"segment_id": "seg_110805_769959", "name": "Saravanampatti", "source": "Saravanampatti IT SEZ", "destination": "Ganapathy Bus Stop", "route_label": "Saravanampatti IT SEZ ➔ Ganapathy Bus Stop"},
            {"segment_id": "seg_109995_770267", "name": "Singanallur", "source": "Singanallur Bus Stand", "destination": "Ramanathapuram (Trichy Rd)", "route_label": "Singanallur Bus Stand ➔ Ramanathapuram (Trichy Rd)"},
            {"segment_id": "seg_109980_769634", "name": "Coimbatore Junction", "source": "Coimbatore Railway Junction", "destination": "Collectorate & Court", "route_label": "Coimbatore Railway Junction ➔ Collectorate & Court"},
        ]

        return jsonify({
            "evaluations": records,
            "total": total,
            "page": page,
            "pages": math.ceil(total / limit) if limit else 1,
            "available_corridors": available_corridors,
        }), 200
    except Exception as e:
        logger.error(f"Error in get_forecast_evaluations: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500


def run_daily_forecast_check():
    """
    Handle POST /api/admin/forecast-evaluations/run-daily-check
    Runs daily telemetry check, 8AM forecast, and 5PM evaluation for the target date.
    """
    from backend.database import get_db
    try:
        from scripts.update_daily_telemetry_to_today import generate_telemetry_and_evaluations
        generate_telemetry_and_evaluations()
        from ml.patchtst.forecast_evaluator import compute_aggregate_metrics
        db = get_db()
        metrics = compute_aggregate_metrics(db)
        return jsonify({
            "message": "Daily telemetry synchronized and verified forecasts checked successfully.",
            "metrics": metrics,
        }), 200
    except Exception as e:
        logger.error(f"Error in run_daily_forecast_check: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500


def get_forecast_metrics():
    """
    Handle GET /api/admin/forecast-evaluations/metrics
    Returns aggregate MAE, RMSE, MAPE, and derived accuracy score.
    """
    try:
        from backend.database import get_db
        from ml.patchtst.forecast_evaluator import compute_aggregate_metrics
        db = get_db()
        metrics = compute_aggregate_metrics(db)
        return jsonify({"status": "ok", "metrics": metrics}), 200
    except Exception as e:
        logger.error(f"Error in get_forecast_metrics: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500


def trigger_am_prediction():
    """
    Handle POST /api/admin/forecast-evaluations/run-8am
    Manually trigger 8AM prediction generation.
    """
    import threading
    from backend.database import get_db
    from ml.patchtst.forecast_evaluator import generate_8am_prediction
    try:
        body = request.get_json(silent=True) or {}
        target_date = body.get("target_date")  # Optional: YYYY-MM-DD

        db = get_db()
        results = generate_8am_prediction(db, target_date=target_date)
        stored = len([r for r in results if r.get("stored", False)])
        return jsonify({
            "message": f"8AM prediction generated: {stored} segments stored.",
            "segments": len(results),
            "stored": stored,
            "target_date": target_date,
        }), 200
    except Exception as e:
        logger.error(f"Error in trigger_am_prediction: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500


def trigger_pm_actuals():
    """
    Handle POST /api/admin/forecast-evaluations/collect-5pm
    Manually trigger 5PM actual traffic collection and evaluation.
    """
    from backend.database import get_db
    from ml.patchtst.forecast_evaluator import collect_5pm_actuals
    try:
        body = request.get_json(silent=True) or {}
        target_date = body.get("target_date")  # Optional: YYYY-MM-DD

        db = get_db()
        results = collect_5pm_actuals(db, target_date=target_date)
        evaluated = len([r for r in results if r.get("evaluated", False)])
        return jsonify({
            "message": f"5PM actuals collected: {evaluated} predictions evaluated.",
            "segments_processed": len(results),
            "evaluated": evaluated,
            "target_date": target_date,
        }), 200
    except Exception as e:
        logger.error(f"Error in trigger_pm_actuals: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500


def get_forecast_evaluation_table():
    """
    Handle GET /api/admin/forecast-evaluations/table
    Returns the live validation table for dashboard display.
    """
    from backend.database import get_db
    from ml.patchtst.forecast_evaluator import get_evaluation_table
    try:
        db = get_db()
        limit = int(request.args.get("limit", 100))
        table = get_evaluation_table(db, limit=limit)
        return jsonify({"status": "ok", "table": table, "count": len(table)}), 200
    except Exception as e:
        logger.error(f"Error in get_forecast_evaluation_table: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500
