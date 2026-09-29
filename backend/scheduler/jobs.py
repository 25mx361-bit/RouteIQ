"""
backend/scheduler/jobs.py — Scheduled Background Data Collection & Monitoring Jobs.

Defined Scheduled Tasks:
  1. traffic_data_collection() — every 15 min: Collects TomTom flow across Coimbatore corridors
  2. weather_data_collection() — every 15 min: Collects Open-Meteo current telemetry
  3. event_status_update()     — every 1 hour: Expires ended traffic events & hazards
  4. notification_check()      — every 5 min: Scans for active landslide hazards and pending alerts

All runs are logged to MongoDB system_logs with start/end time, record counts, and errors.
NOTE: Machine learning retraining is deliberately excluded (Admin-triggered only).
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List
from loguru import logger

from backend.database import get_db
from backend.repositories.system_log_repository import SystemLogRepository
from backend.repositories.traffic_repository import TrafficRepository
from backend.repositories.weather_repository import WeatherRepository
from backend.repositories.event_repository import EventRepository
from backend.repositories.landslide_repository import LandslideRepository
from backend.repositories.notification_repository import NotificationRepository
from backend.services.traffic_service import TrafficService
from backend.services.weather_service import WeatherService

# Monitored High-Priority Corridors in Coimbatore
COIMBATORE_MONITORED_HUBS = [
    {"name": "Gandhipuram Hub", "lat": 11.0168, "lng": 76.9558},
    {"name": "RS Puram Commercial Center", "lat": 11.0094, "lng": 76.9458},
    {"name": "Coimbatore Junction", "lat": 10.9980, "lng": 76.9634},
    {"name": "PSG Tech Peelamedu", "lat": 11.0244, "lng": 77.0028},
    {"name": "Coimbatore Airport Corridor", "lat": 11.0298, "lng": 77.0434},
    {"name": "Saravanampatti Tech Zone", "lat": 11.0805, "lng": 76.9959},
    {"name": "Singanallur Junction", "lat": 10.9995, "lng": 77.0267},
    {"name": "Ukkadam South Bus Terminus", "lat": 10.9892, "lng": 76.9613},
]

# In-memory execution telemetry for instant admin status reporting
JOB_TELEMETRY: Dict[str, Dict[str, Any]] = {
    "traffic_data_collection": {
        "job_id": "traffic_data_collection",
        "description": "TomTom Traffic Flow Segment Collection (Coimbatore Arterials)",
        "interval": "15 minutes",
        "last_run_time": None,
        "last_duration_ms": 0,
        "last_records_collected": 0,
        "last_status": "PENDING",
        "last_error": None,
    },
    "weather_data_collection": {
        "job_id": "weather_data_collection",
        "description": "Open-Meteo Atmospheric Telemetry & Risk Collection",
        "interval": "15 minutes",
        "last_run_time": None,
        "last_duration_ms": 0,
        "last_records_collected": 0,
        "last_status": "PENDING",
        "last_error": None,
    },
    "event_status_update": {
        "job_id": "event_status_update",
        "description": "Traffic Event & Road Closure Expiry Synchronisation",
        "interval": "1 hour",
        "last_run_time": None,
        "last_duration_ms": 0,
        "last_records_collected": 0,
        "last_status": "PENDING",
        "last_error": None,
    },
    "notification_check": {
        "job_id": "notification_check",
        "description": "Landslide Hazard & Adverse Weather Alert Dispatcher",
        "interval": "5 minutes",
        "last_run_time": None,
        "last_duration_ms": 0,
        "last_records_collected": 0,
        "last_status": "PENDING",
        "last_error": None,
    },
    "am_prediction_job": {
        "job_id": "am_prediction_job",
        "description": "8AM PatchTST Future Traffic Prediction Generator",
        "interval": "daily at 08:00 IST",
        "last_run_time": None,
        "last_duration_ms": 0,
        "last_records_collected": 0,
        "last_status": "PENDING",
        "last_error": None,
    },
    "pm_actuals_job": {
        "job_id": "pm_actuals_job",
        "description": "5PM Actual Traffic Collection & Prediction Evaluation",
        "interval": "daily at 17:00 IST",
        "last_run_time": None,
        "last_duration_ms": 0,
        "last_records_collected": 0,
        "last_status": "PENDING",
        "last_error": None,
    },
}


def _record_job_log(
    job_id: str,
    start_time: float,
    records_count: int,
    status: str,
    error_msg: str | None = None,
    extra_details: Dict[str, Any] | None = None,
):
    """Update in-memory telemetry and persist structured audit record to MongoDB system_logs."""
    end_time = time.time()
    duration_ms = round((end_time - start_time) * 1000, 1)
    iso_now = datetime.now(timezone.utc).isoformat()

    # Update in-memory telemetry
    if job_id in JOB_TELEMETRY:
        JOB_TELEMETRY[job_id].update({
            "last_run_time": iso_now,
            "last_duration_ms": duration_ms,
            "last_records_collected": records_count,
            "last_status": status,
            "last_error": error_msg,
        })

    # Persist to MongoDB system_logs collection
    try:
        db = get_db()
        sys_repo = SystemLogRepository(db)
        sys_repo.log(
            level="INFO" if status == "SUCCESS" else "ERROR",
            source=f"scheduler.{job_id}",
            message=f"Scheduled job '{job_id}' executed with status={status} ({records_count} records in {duration_ms}ms)",
            details={
                "job_id": job_id,
                "status": status,
                "records_collected": records_count,
                "duration_ms": duration_ms,
                "error": error_msg,
                **(extra_details or {}),
            },
        )
    except Exception as e:
        logger.warning(f"Could not persist scheduler audit log to MongoDB: {e}")


def traffic_data_collection() -> Dict[str, Any]:
    """
    Job 1: Collect TomTom flow segment data for known Coimbatore corridors every 15 minutes.
    """
    job_id = "traffic_data_collection"
    start_t = time.time()
    logger.info(f"Starting scheduled job: {job_id}")

    records_collected = 0
    errors: List[str] = []

    try:
        db = get_db()
        traffic_service = TrafficService(traffic_repo=TrafficRepository(db))

        for hub in COIMBATORE_MONITORED_HUBS:
            try:
                flow = traffic_service.get_flow_at_point(
                    lat=hub["lat"], lng=hub["lng"], zoom=10, persist=True
                )
                if flow:
                    records_collected += 1
            except Exception as hub_err:
                err_str = f"Error collecting traffic for {hub['name']}: {hub_err}"
                logger.warning(err_str)
                errors.append(err_str)

        status = "SUCCESS" if not errors else ("PARTIAL" if records_collected > 0 else "ERROR")
        _record_job_log(
            job_id=job_id,
            start_time=start_t,
            records_count=records_collected,
            status=status,
            error_msg="; ".join(errors) if errors else None,
            extra_details={"hubs_targeted": len(COIMBATORE_MONITORED_HUBS)},
        )
        logger.info(f"Completed scheduled job {job_id}: {records_collected} records stored.")
        return {"status": status, "records_collected": records_collected}

    except Exception as e:
        logger.error(f"Fatal error in scheduled job {job_id}: {e}")
        _record_job_log(job_id, start_t, 0, "ERROR", str(e))
        return {"status": "ERROR", "error": str(e)}


def weather_data_collection() -> Dict[str, Any]:
    """
    Job 2: Collect Open-Meteo atmospheric telemetry and calculate risk scores every 15 minutes.
    """
    job_id = "weather_data_collection"
    start_t = time.time()
    logger.info(f"Starting scheduled job: {job_id}")

    records_collected = 0
    errors: List[str] = []

    try:
        db = get_db()
        weather_service = WeatherService(weather_repo=WeatherRepository(db))

        # Sample Coimbatore North, South, East, and Central stations
        weather_points = [
            {"name": "Coimbatore Central (Gandhipuram)", "lat": 11.0168, "lng": 76.9558},
            {"name": "Coimbatore East (Airport/Peelamedu)", "lat": 11.0298, "lng": 77.0434},
            {"name": "Coimbatore North (Saravanampatti)", "lat": 11.0805, "lng": 76.9959},
            {"name": "Coimbatore South (Ukkadam/Sundarapuram)", "lat": 10.9892, "lng": 76.9613},
        ]

        for pt in weather_points:
            try:
                weather = weather_service.get_current_weather(
                    lat=pt["lat"], lng=pt["lng"], persist=True
                )
                if weather:
                    records_collected += 1
            except Exception as pt_err:
                err_str = f"Error collecting weather for {pt['name']}: {pt_err}"
                logger.warning(err_str)
                errors.append(err_str)

        status = "SUCCESS" if not errors else ("PARTIAL" if records_collected > 0 else "ERROR")
        _record_job_log(
            job_id=job_id,
            start_time=start_t,
            records_count=records_collected,
            status=status,
            error_msg="; ".join(errors) if errors else None,
            extra_details={"stations_targeted": len(weather_points)},
        )
        logger.info(f"Completed scheduled job {job_id}: {records_collected} records stored.")
        return {"status": status, "records_collected": records_collected}

    except Exception as e:
        logger.error(f"Fatal error in scheduled job {job_id}: {e}")
        _record_job_log(job_id, start_t, 0, "ERROR", str(e))
        return {"status": "ERROR", "error": str(e)}


def event_status_update() -> Dict[str, Any]:
    """
    Job 3: Check and update event status (mark expired events past end_time) every 1 hour.
    """
    job_id = "event_status_update"
    start_t = time.time()
    logger.info(f"Starting scheduled job: {job_id}")

    try:
        db = get_db()
        now = datetime.now(timezone.utc)

        # Update events whose end_time has passed
        result = db.events.update_many(
            {"end_time": {"$lte": now}, "is_active": {"$ne": False}},
            {"$set": {"is_active": False, "status": "EXPIRED", "updated_at": now}},
        )
        modified_count = result.modified_count

        _record_job_log(
            job_id=job_id,
            start_time=start_t,
            records_count=modified_count,
            status="SUCCESS",
            extra_details={"expired_events_count": modified_count},
        )
        logger.info(f"Completed scheduled job {job_id}: {modified_count} expired events updated.")
        return {"status": "SUCCESS", "records_updated": modified_count}

    except Exception as e:
        logger.error(f"Error in scheduled job {job_id}: {e}")
        _record_job_log(job_id, start_t, 0, "ERROR", str(e))
        return {"status": "ERROR", "error": str(e)}


def notification_check() -> Dict[str, Any]:
    """
    Job 4: Scan for active high-risk landslide hazard alerts and dispatch notifications every 5 minutes.
    """
    job_id = "notification_check"
    start_t = time.time()
    logger.info(f"Starting scheduled job: {job_id}")

    try:
        db = get_db()
        landslide_repo = LandslideRepository(db)
        notif_repo = NotificationRepository(db)

        active_landslides = landslide_repo.get_active_landslides()
        dispatched_count = 0

        # Check for High or Severe risk landslides and notify admin / users
        high_risk_landslides = [
            l for l in active_landslides if l.get("risk_level") in ("High", "Severe")
        ]

        if high_risk_landslides:
            for hazard in high_risk_landslides:
                title = f"Landslide Alert: {hazard.get('title', 'Ghat Section Alert')}"
                existing = db.notifications.find_one({
                    "title": title,
                    "metadata.landslide_id": str(hazard.get("_id", "")),
                })
                if not existing:
                    notif_repo.create({
                        "user_id": "broadcast_all",
                        "title": title,
                        "message": f"Hazard Risk: {hazard.get('risk_level')}. Caution advised near {hazard.get('region_name', 'Western Ghats Corridor')}.",
                        "type": "hazard_alert",
                        "is_read": False,
                        "metadata": {"landslide_id": str(hazard.get("_id", ""))},
                    })
                    dispatched_count += 1

        _record_job_log(
            job_id=job_id,
            start_time=start_t,
            records_count=dispatched_count,
            status="SUCCESS",
            extra_details={
                "active_hazards": len(active_landslides),
                "high_risk_hazards": len(high_risk_landslides),
            },
        )
        logger.info(f"Completed scheduled job {job_id}: {dispatched_count} alerts dispatched.")
        return {"status": "SUCCESS", "alerts_dispatched": dispatched_count}

    except Exception as e:
        logger.error(f"Error in scheduled job {job_id}: {e}")
        _record_job_log(job_id, start_t, 0, "ERROR", str(e))
        return {"status": "ERROR", "error": str(e)}


def am_prediction_job() -> Dict[str, Any]:
    """
    Job 5: Daily 8AM — Generate PatchTST predictions for 5PM target time.
    Stores predictions in forecast_evaluations collection.
    Only runs if PatchTST model is trained (checkpoint exists).
    """
    job_id = "am_prediction_job"
    start_t = time.time()
    logger.info(f"Starting scheduled job: {job_id}")

    try:
        from ml.patchtst.forecast_evaluator import generate_8am_prediction
        from ml.patchtst.config import PatchTSTConfig

        cfg = PatchTSTConfig()
        if not cfg.model_path.exists() and not cfg.legacy_model_path.exists():
            logger.warning("8AM prediction job skipped: no trained PatchTST model found.")
            _record_job_log(job_id, start_t, 0, "SKIPPED", "No trained model checkpoint found.")
            return {"status": "SKIPPED", "message": "No trained model found"}

        db = get_db()
        from datetime import date
        today_str = date.today().isoformat()
        results = generate_8am_prediction(db, target_date=today_str)
        records_stored = len([r for r in results if r.get("stored", False)])

        _record_job_log(
            job_id=job_id,
            start_time=start_t,
            records_count=records_stored,
            status="SUCCESS",
            extra_details={"target_date": today_str, "segments_predicted": len(results)},
        )
        logger.info(f"8AM prediction job: {records_stored} predictions stored for {today_str}.")
        return {"status": "SUCCESS", "records_stored": records_stored, "target_date": today_str}

    except Exception as e:
        logger.error(f"Fatal error in {job_id}: {e}")
        _record_job_log(job_id, start_t, 0, "ERROR", str(e))
        return {"status": "ERROR", "error": str(e)}


def pm_actuals_job() -> Dict[str, Any]:
    """
    Job 6: Daily 5PM — Collect actual live TomTom traffic and evaluate 8AM predictions.
    Matches actual observations to stored forecast_evaluations records.
    Calculates and stores absolute error and percentage error.
    """
    job_id = "pm_actuals_job"
    start_t = time.time()
    logger.info(f"Starting scheduled job: {job_id}")

    try:
        from ml.patchtst.forecast_evaluator import collect_5pm_actuals
        from datetime import date

        db = get_db()
        today_str = date.today().isoformat()

        # First collect fresh TomTom data for all monitored hubs
        traffic_service = TrafficService(traffic_repo=TrafficRepository(db))
        for hub in COIMBATORE_MONITORED_HUBS:
            try:
                traffic_service.get_flow_at_point(
                    lat=hub["lat"], lng=hub["lng"], zoom=10, persist=True
                )
            except Exception as hub_err:
                logger.warning(f"Error collecting 5PM traffic for {hub['name']}: {hub_err}")

        # Now match actuals to predictions
        results = collect_5pm_actuals(db, target_date=today_str)
        evaluated_count = len([r for r in results if r.get("evaluated", False)])

        _record_job_log(
            job_id=job_id,
            start_time=start_t,
            records_count=evaluated_count,
            status="SUCCESS",
            extra_details={"target_date": today_str, "segments_evaluated": evaluated_count},
        )
        logger.info(f"5PM actuals job: {evaluated_count} predictions evaluated for {today_str}.")
        return {"status": "SUCCESS", "records_evaluated": evaluated_count, "target_date": today_str}

    except Exception as e:
        logger.error(f"Fatal error in {job_id}: {e}")
        _record_job_log(job_id, start_t, 0, "ERROR", str(e))
        return {"status": "ERROR", "error": str(e)}

