"""
ml/catboost/features.py — Feature list for CatBoost.

This list MUST exactly match the keys produced by
backend.services.feature_engineering_service.build_route_feature_vector().

If you add a feature to build_route_feature_vector, add it here too.
If you remove a feature, remove it here too.
"""
from __future__ import annotations
from typing import List

# ── Numeric Features ────────────────────────────────────────────────────────
NUMERIC_FEATURES: List[str] = [
    # Route basics
    "distance_km",
    "duration_min",
    "num_waypoints",
    # Traffic / TCI
    "tci",
    "predicted_travel_time",
    "free_flow_travel_time",
    "predicted_speed",
    "predicted_flow",
    # Datetime
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    # Weather
    "weather_risk_score",
    "temperature",
    "precipitation",
    "wind_speed",
    "visibility",
    "humidity",
    "surface_pressure",
    # Events (aggregate)
    "event_impact_score",
    "event_delay_multiplier",
    "num_active_events",
    # Festival-specific
    "festival_indicator",
    "festival_impact_score",
    "festival_distance_km",
    "festival_active",
    # Marriage-specific
    "marriage_event_indicator",
    "marriage_impact_score",
    "marriage_distance_km",
    "marriage_active",
    # Landslide
    "landslide_indicator",
    "landslide_active",
    "landslide_distance_km",
    "road_blocked",
]

# ── Categorical Features ─────────────────────────────────────────────────────
CATEGORICAL_FEATURES: List[str] = [
    "weather_risk_level",       # "Low" | "Moderate" | "High" | "Severe"
    "landslide_severity",       # "NONE" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
]

# ── All Features (order matters — matches CatBoost Pool column order) ────────
ALL_FEATURES: List[str] = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# ── Target Column ────────────────────────────────────────────────────────────
TARGET_COLUMN: str = "label"

# ── Categorical feature indices in ALL_FEATURES ──────────────────────────────
CAT_FEATURE_INDICES: List[int] = [
    ALL_FEATURES.index(f) for f in CATEGORICAL_FEATURES
]
