"""
backend/scheduler/scheduler.py — APScheduler Manager for Background Data Collection.

Handles:
  - Initializing and configuring APScheduler BackgroundScheduler
  - Registering periodic collection tasks (Traffic, Weather, Event Expiry, Notification Check)
  - Starting scheduler on Flask app startup and graceful teardown on exit
  - Exposing administrative status telemetry for GET /api/admin/scheduler/status
"""
from __future__ import annotations

import atexit
from typing import Any, Dict, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from backend.scheduler.jobs import (
    traffic_data_collection,
    weather_data_collection,
    event_status_update,
    notification_check,
    JOB_TELEMETRY,
)

# Global BackgroundScheduler instance
scheduler: Optional[BackgroundScheduler] = None
_is_initialized = False


def init_scheduler(app=None) -> BackgroundScheduler:
    """Initialize APScheduler instance and register background collection jobs."""
    global scheduler, _is_initialized
    if _is_initialized and scheduler is not None:
        return scheduler

    scheduler = BackgroundScheduler(
        daemon=True,
        timezone="Asia/Kolkata",
    )

    # 1. Traffic Data Collection (every 15 minutes)
    scheduler.add_job(
        func=traffic_data_collection,
        trigger=IntervalTrigger(minutes=15),
        id="traffic_data_collection",
        name="TomTom Traffic Flow Collection (15m)",
        replace_existing=True,
        max_instances=1,
    )

    # 2. Weather Data Collection (every 15 minutes)
    scheduler.add_job(
        func=weather_data_collection,
        trigger=IntervalTrigger(minutes=15),
        id="weather_data_collection",
        name="Open-Meteo Weather Collection (15m)",
        replace_existing=True,
        max_instances=1,
    )

    # 3. Event Status Update & Expiry (every 1 hour)
    scheduler.add_job(
        func=event_status_update,
        trigger=IntervalTrigger(hours=1),
        id="event_status_update",
        name="Event Status & Expiry Check (1h)",
        replace_existing=True,
        max_instances=1,
    )

    # 4. Landslide Notification Check (every 5 minutes)
    scheduler.add_job(
        func=notification_check,
        trigger=IntervalTrigger(minutes=5),
        id="notification_check",
        name="Hazard Alert & Notification Scanner (5m)",
        replace_existing=True,
        max_instances=1,
    )

    _is_initialized = True
    logger.info("APScheduler initialized with 4 periodic data collection tasks.")

    # Graceful shutdown on Python process termination
    atexit.register(shutdown_scheduler)

    return scheduler


def start_scheduler() -> bool:
    """Start the background scheduler if not already running."""
    global scheduler
    if scheduler is None:
        init_scheduler()

    if scheduler and not scheduler.running:
        try:
            scheduler.start()
            logger.info("APScheduler background engine started successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to start APScheduler: {e}")
            return False
    return True


def shutdown_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    global scheduler
    if scheduler and scheduler.running:
        logger.info("Shutting down APScheduler...")
        try:
            scheduler.shutdown(wait=False)
            logger.info("APScheduler shut down cleanly.")
        except Exception as e:
            logger.warning(f"Notice during APScheduler shutdown: {e}")


def get_scheduler_status() -> Dict[str, Any]:
    """
    Retrieve comprehensive scheduler state, running status, and per-job telemetry.
    Used by GET /api/admin/scheduler/status endpoint.
    """
    global scheduler
    is_running = bool(scheduler and scheduler.running)

    job_list: List[Dict[str, Any]] = []

    if scheduler:
        for job in scheduler.get_jobs():
            t_data = JOB_TELEMETRY.get(job.id, {})
            next_run = job.next_run_time.isoformat() if job.next_run_time else None
            job_list.append({
                "job_id": job.id,
                "name": job.name,
                "interval": t_data.get("interval", "N/A"),
                "description": t_data.get("description", ""),
                "next_run_time": next_run,
                "last_run_time": t_data.get("last_run_time"),
                "last_duration_ms": t_data.get("last_duration_ms", 0),
                "last_records_collected": t_data.get("last_records_collected", 0),
                "last_status": t_data.get("last_status", "PENDING"),
                "last_error": t_data.get("last_error"),
            })
    else:
        # Fallback to telemetry dict if scheduler instance not yet instantiated
        for j_id, t_data in JOB_TELEMETRY.items():
            job_list.append({
                "job_id": j_id,
                "name": j_id.replace("_", " ").title(),
                "interval": t_data.get("interval", "N/A"),
                "description": t_data.get("description", ""),
                "next_run_time": None,
                "last_run_time": t_data.get("last_run_time"),
                "last_duration_ms": t_data.get("last_duration_ms", 0),
                "last_records_collected": t_data.get("last_records_collected", 0),
                "last_status": t_data.get("last_status", "PENDING"),
                "last_error": t_data.get("last_error"),
            })

    return {
        "scheduler_status": "ACTIVE" if is_running else "IDLE",
        "running": is_running,
        "timezone": "Asia/Kolkata",
        "total_jobs": len(job_list),
        "jobs": job_list,
    }
