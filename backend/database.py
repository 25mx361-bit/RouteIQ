"""
database.py — Pure PyMongo client initialisation for RouteIQ (No ORM / ODM).

Usage (inside a Flask app, repository, or standalone script):
    from backend.database import get_db, init_db, db

    # standalone / test
    init_db("mongodb://localhost:27017/routeiq")

    # direct db access
    db.users.find_one(...)
"""
from __future__ import annotations

import os
from typing import Optional

from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.database import Database
from pymongo.errors import OperationFailure
from loguru import logger

# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
_client: Optional[MongoClient] = None
_db: Optional[Database] = None


class _DatabaseProxy:
    """Proxy object allowing `from backend.database import db` with lazy initialization."""

    def __getattr__(self, name: str):
        return getattr(get_db(), name)

    def __getitem__(self, name: str):
        return get_db()[name]


db: Database = _DatabaseProxy()  # type: ignore[assignment]


def init_db(mongo_uri: Optional[str] = None) -> Database:
    """
    Initialise the MongoClient and create all collection indexes.

    Args:
        mongo_uri: Full MongoDB connection string. If omitted, MONGO_URI env-var is used.

    Returns:
        pymongo.database.Database instance.
    """
    global _client, _db

    uri = mongo_uri or os.getenv("MONGO_URI", "mongodb://localhost:27017/routeiq")
    if not uri:
        raise ValueError(
            "MONGO_URI must be provided either as an argument or as an environment variable."
        )

    db_name = _extract_db_name(uri)

    logger.info(f"Connecting to MongoDB — db={db_name}")
    _client = MongoClient(uri, serverSelectionTimeoutMS=5_000)

    # Ping to verify connection
    _client.admin.command("ping")
    logger.info("MongoDB connection established.")

    _db = _client[db_name]
    _create_indexes(_db)
    return _db


def get_db() -> Database:
    """
    Return the active database instance, initializing from MONGO_URI if not yet connected.
    """
    global _db
    if _db is None:
        init_db()
    return _db


def close_db() -> None:
    """Close the MongoDB connection (useful in tests and teardown)."""
    global _client, _db
    if _client:
        _client.close()
        logger.info("MongoDB connection closed.")
    _client = None
    _db = None


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _extract_db_name(uri: str) -> str:
    """Extract database name from MongoDB URI, defaulting to 'routeiq'."""
    try:
        path = uri.split("/")[-1].split("?")[0]
        return path if path else "routeiq"
    except Exception:
        return "routeiq"


def _safe_create_index(collection, keys, **kwargs):
    """Safely create index ignoring pre-existing name or equivalent index conflicts."""
    try:
        collection.create_index(keys, **kwargs)
    except OperationFailure as e:
        if "already exists" in str(e) or e.code in (85, 86):
            logger.debug(f"Index {keys} already exists: {e}")
        else:
            logger.warning(f"Could not create index {keys}: {e}")
    except Exception as e:
        logger.warning(f"Error creating index on {collection.name}: {e}")


def _create_indexes(target_db: Database) -> None:
    """
    Create all required indexes across every RouteIQ collection.
    """
    logger.debug("Creating/verifying MongoDB indexes …")

    # 1. users
    _safe_create_index(target_db.users, [("email", ASCENDING)], unique=True, name="idx_users_email")
    _safe_create_index(target_db.users, [("created_at", DESCENDING)], name="idx_users_created_at")

    # 2. traffic_data
    _safe_create_index(
        target_db.traffic_data,
        [("segment_id", ASCENDING), ("timestamp", DESCENDING)],
        name="idx_traffic_segment_time",
    )
    _safe_create_index(target_db.traffic_data, [("timestamp", DESCENDING)], name="idx_traffic_time")
    _safe_create_index(target_db.traffic_data, [("road_id", ASCENDING)], name="idx_traffic_road")

    # 3. weather_data
    _safe_create_index(
        target_db.weather_data,
        [("timestamp", DESCENDING), ("lat", ASCENDING), ("lng", ASCENDING)],
        name="idx_weather_time_location",
    )

    # 4. routes
    _safe_create_index(target_db.routes, [("user_id", ASCENDING)], name="idx_routes_user")
    _safe_create_index(target_db.routes, [("fetched_at", DESCENDING)], name="idx_routes_fetched")
    _safe_create_index(
        target_db.routes,
        [("source_label", TEXT), ("destination_label", TEXT)],
        name="idx_routes_text",
    )

    # 5. predictions
    _safe_create_index(target_db.predictions, [("user_id", ASCENDING)], name="idx_pred_user")
    _safe_create_index(
        target_db.predictions,
        [("user_id", ASCENDING), ("created_at", DESCENDING)],
        name="idx_pred_user_time",
    )

    # 6. events
    _safe_create_index(target_db.events, [("timestamp", DESCENDING)], name="idx_events_time")
    _safe_create_index(target_db.events, [("location", "2dsphere")], name="idx_events_geo")

    # 7. landslides
    _safe_create_index(target_db.landslides, [("reported_at", DESCENDING)], name="idx_landslide_time")
    _safe_create_index(target_db.landslides, [("location", "2dsphere")], name="idx_landslide_geo")

    # 8. notifications
    _safe_create_index(
        target_db.notifications,
        [("user_id", ASCENDING), ("created_at", DESCENDING)],
        name="idx_notif_user_time",
    )
    _safe_create_index(target_db.notifications, [("is_read", ASCENDING)], name="idx_notif_read")

    # 9. search_history
    _safe_create_index(
        target_db.search_history,
        [("user_id", ASCENDING), ("searched_at", DESCENDING)],
        name="idx_search_user_time",
    )

    # 10. model_logs
    _safe_create_index(target_db.model_logs, [("model_name", ASCENDING)], name="idx_mlog_model")
    _safe_create_index(target_db.model_logs, [("logged_at", DESCENDING)], name="idx_mlog_time")

    # 11. system_logs
    _safe_create_index(target_db.system_logs, [("level", ASCENDING)], name="idx_syslog_level")
    _safe_create_index(target_db.system_logs, [("timestamp", DESCENDING)], name="idx_syslog_time")
    _safe_create_index(
        target_db.system_logs,
        [("created_at", ASCENDING)],
        expireAfterSeconds=30 * 24 * 3600,
        name="idx_syslog_ttl",
    )

    # 12. forecast_evaluations
    _safe_create_index(
        target_db.forecast_evaluations,
        [("prediction_date", ASCENDING), ("segment_id", ASCENDING)],
        name="idx_forecast_date_segment",
    )
    _safe_create_index(
        target_db.forecast_evaluations,
        [("evaluated", ASCENDING), ("prediction_date", DESCENDING)],
        name="idx_forecast_eval_date",
    )
    _safe_create_index(
        target_db.forecast_evaluations,
        [("created_at", DESCENDING)],
        name="idx_forecast_created",
    )

    logger.info("All 12 MongoDB collection indexes verified.")
