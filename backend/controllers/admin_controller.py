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

