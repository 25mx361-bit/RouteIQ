"""
tests/test_feature_engineering.py — Feature Engineering Service Test Suite.

Tests:
  1. calculate_tci — normal, zero free_flow edge case
  2. calculate_weather_risk — delegates, returns risk_score and risk_level
  3. calculate_landslide_features — blocked vs non-blocked scenarios
  4. calculate_festival_features — FESTIVAL type detection
  5. calculate_marriage_features — MARRIAGE type detection
  6. build_route_feature_vector — full integration, correct keys and types
"""
import sys
from pathlib import Path
from datetime import datetime, timezone

current = Path(__file__).resolve()
for p in [current.parent, current.parent.parent]:
    if (p / "backend").exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

from backend.services.feature_engineering_service import (
    calculate_tci,
    calculate_weather_risk,
    calculate_landslide_features,
    calculate_festival_features,
    calculate_marriage_features,
    build_route_feature_vector,
)

# ──────────────────────────────────────────────────────────────────────────────
# Shared fixtures
# ──────────────────────────────────────────────────────────────────────────────

COIMBATORE_ROUTE_COORDS = [
    [11.0168, 76.9558],  # Gandhipuram [lat, lng]
    [11.0140, 76.9510],
    [11.0120, 76.9490],
    [11.0100, 76.9470],
    [11.0094, 76.9458],  # R.S. Puram
]

SAMPLE_WEATHER = {
    "temperature_2m": 32.5,
    "precipitation": 5.2,
    "visibility": 6500.0,
    "wind_speed_10m": 18.0,
    "relative_humidity_2m": 75.0,
    "surface_pressure": 1008.0,
}

SAMPLE_ROUTE = {
    "coordinates": COIMBATORE_ROUTE_COORDS,
    "distance_km": 4.3,
    "duration_min": 12.0,
    "free_flow_travel_time": 600.0,  # seconds (10 min free flow)
}

ACTIVE_LANDSLIDE_NEAR = {
    "_id": "ls001",
    "title": "Coonoor Ghat Debris Flow",
    "status": "ACTIVE",
    "is_active": True,
    "severity": "HIGH",
    "risk_level": "High",
    "region_name": "Mettupalayam-Coonoor Ghat",
    "road_name": "NH-181",
    "lat": 11.0145,
    "lng": 76.9505,
    "radius_m": 5000.0,
    "location": {"type": "Point", "coordinates": [76.9505, 11.0145]},
}

ACTIVE_LANDSLIDE_FAR = {
    "_id": "ls002",
    "title": "Valparai Landslide",
    "status": "ACTIVE",
    "is_active": True,
    "severity": "MEDIUM",
    "lat": 10.3261,
    "lng": 76.9634,
    "radius_m": 500.0,
    "location": {"type": "Point", "coordinates": [76.9634, 10.3261]},
}

FESTIVAL_EVENT = {
    "_id": "ev001",
    "title": "Kaveri Mahotsav Gandhipuram",
    "event_type": "FESTIVAL",
    "impact_level": "HIGH",
    "expected_crowd": 25000,
    "start_time": "2026-08-25T09:00:00Z",
    "end_time": "2026-08-25T22:00:00Z",
    "venue_lat": 11.0165,
    "venue_lng": 76.9560,
}

MARRIAGE_EVENT = {
    "_id": "ev002",
    "title": "Kalaivani-Rajesh Wedding",
    "event_type": "MARRIAGE",
    "impact_level": "MEDIUM",
    "expected_crowd": 800,
    "start_time": "2026-08-25T10:00:00Z",
    "end_time": "2026-08-25T18:00:00Z",
    "venue_lat": 11.0150,
    "venue_lng": 76.9530,
}

TARGET_DT = datetime(2026, 8, 25, 12, 0, 0, tzinfo=timezone.utc)

SAMPLE_PREDICTIONS = {
    "predicted_travel_time": 780.0,  # 13 min — slower than free flow
    "predicted_speed": 32.5,
    "predicted_flow": 1200.0,
}


# ──────────────────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_1_tci_normal():
    print("\n--- 1. TCI — Normal Calculation ---")
    tci = calculate_tci(780.0, 600.0)
    assert tci == round(780.0 / 600.0, 4), f"Expected 1.3, got {tci}"
    print(f" [PASS] TCI = {tci} (expected ~1.3 — moderate congestion)")


def test_2_tci_zero_denominator():
    print("\n--- 2. TCI — Zero Free-Flow Edge Case ---")
    tci = calculate_tci(780.0, 0.0)
    assert tci == 999.0, f"Expected 999.0, got {tci}"
    print(f" [PASS] TCI = {tci} (complete blockage sentinel)")


def test_3_weather_risk():
    print("\n--- 3. Weather Risk — Delegation to weather_risk_calculator ---")
    result = calculate_weather_risk(SAMPLE_WEATHER)
    assert "risk_score" in result, "Missing risk_score key"
    assert "risk_level" in result, "Missing risk_level key"
    assert isinstance(result["risk_score"], float), "risk_score must be float"
    assert result["risk_level"] in {"Low", "Moderate", "High", "Severe"}, \
        f"Unexpected risk_level: {result['risk_level']}"
    print(f" [PASS] Weather risk_score={result['risk_score']}, level={result['risk_level']}")


def test_4_landslide_features_blocked():
    print("\n--- 4. Landslide Features — Route is BLOCKED by nearby hazard ---")
    result = calculate_landslide_features(COIMBATORE_ROUTE_COORDS, [ACTIVE_LANDSLIDE_NEAR])
    assert result["landslide_indicator"] == 1, "landslide_indicator should be 1"
    assert result["road_blocked"] == 1, "road_blocked should be 1"
    assert result["landslide_severity"] in {"HIGH", "CRITICAL", "MEDIUM", "LOW"}
    print(f" [PASS] landslide_indicator={result['landslide_indicator']}, "
          f"road_blocked={result['road_blocked']}, severity={result['landslide_severity']}, "
          f"dist_km={result['landslide_distance_km']}")


def test_5_landslide_features_none():
    print("\n--- 5. Landslide Features — No active landslides ---")
    result = calculate_landslide_features(COIMBATORE_ROUTE_COORDS, [])
    assert result["landslide_indicator"] == 0
    assert result["road_blocked"] == 0
    assert result["landslide_severity"] == "NONE"
    assert result["landslide_distance_km"] == 999.0
    print(f" [PASS] No hazard: indicator=0, blocked=0, dist=999.0")


def test_6_festival_features():
    print("\n--- 6. Festival Features ---")
    result = calculate_festival_features(
        COIMBATORE_ROUTE_COORDS, TARGET_DT, [FESTIVAL_EVENT, MARRIAGE_EVENT]
    )
    assert "festival_indicator" in result
    assert "festival_impact_score" in result
    assert "festival_distance_km" in result
    assert "festival_active" in result
    assert isinstance(result["festival_indicator"], int)
    print(f" [PASS] festival_indicator={result['festival_indicator']}, "
          f"score={result['festival_impact_score']}, "
          f"dist_km={result['festival_distance_km']}, "
          f"active={result['festival_active']}")


def test_7_marriage_features():
    print("\n--- 7. Marriage Features ---")
    result = calculate_marriage_features(
        COIMBATORE_ROUTE_COORDS, TARGET_DT, [FESTIVAL_EVENT, MARRIAGE_EVENT]
    )
    assert "marriage_event_indicator" in result
    assert "marriage_impact_score" in result
    assert "marriage_distance_km" in result
    assert "marriage_active" in result
    assert isinstance(result["marriage_event_indicator"], int)
    print(f" [PASS] marriage_event_indicator={result['marriage_event_indicator']}, "
          f"score={result['marriage_impact_score']}, "
          f"dist_km={result['marriage_distance_km']}, "
          f"active={result['marriage_active']}")


def test_8_build_route_feature_vector():
    print("\n--- 8. build_route_feature_vector — Full Integration ---")
    vec = build_route_feature_vector(
        route=SAMPLE_ROUTE,
        predictions=SAMPLE_PREDICTIONS,
        weather=SAMPLE_WEATHER,
        events=[FESTIVAL_EVENT, MARRIAGE_EVENT],
        landslides=[ACTIVE_LANDSLIDE_NEAR],
        target_datetime=TARGET_DT,
    )

    required_keys = [
        # Route basics
        "distance_km", "duration_min", "num_waypoints",
        # Traffic
        "tci", "predicted_travel_time", "free_flow_travel_time",
        # Weather
        "weather_risk_score", "weather_risk_level",
        "temperature", "precipitation", "wind_speed", "visibility",
        # Events
        "event_impact_score", "event_delay_multiplier", "num_active_events",
        # Festivals
        "festival_indicator", "festival_impact_score", "festival_distance_km", "festival_active",
        # Marriages
        "marriage_event_indicator", "marriage_impact_score", "marriage_distance_km", "marriage_active",
        # Landslides
        "landslide_indicator", "landslide_active", "landslide_severity",
        "landslide_distance_km", "road_blocked",
        # Datetime
        "hour_of_day", "day_of_week", "is_weekend",
    ]

    missing = [k for k in required_keys if k not in vec]
    assert not missing, f"Missing feature vector keys: {missing}"
    assert vec["tci"] == round(780.0 / 600.0, 4)
    assert vec["road_blocked"] in (0, 1)
    assert vec["hour_of_day"] == 12
    assert vec["is_weekend"] == 0  # 2026-08-25 is a Tuesday

    print(f" [PASS] Feature vector has {len(vec)} keys — all {len(required_keys)} required keys present")
    print(f"        tci={vec['tci']}, road_blocked={vec['road_blocked']}, "
          f"weather_level={vec['weather_risk_level']}, "
          f"festival_indicator={vec['festival_indicator']}, "
          f"marriage_indicator={vec['marriage_event_indicator']}")


# ──────────────────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────────────────

def run_tests():
    print("=================================================================")
    print(" RouteIQ Phase 13: Feature Engineering Service Test Suite")
    print("=================================================================")

    tests = [
        test_1_tci_normal,
        test_2_tci_zero_denominator,
        test_3_weather_risk,
        test_4_landslide_features_blocked,
        test_5_landslide_features_none,
        test_6_festival_features,
        test_7_marriage_features,
        test_8_build_route_feature_vector,
    ]

    failed = []
    for t in tests:
        try:
            t()
        except Exception as exc:
            print(f" [FAIL] {t.__name__}: {exc}")
            failed.append(t.__name__)

    print("\n=================================================================")
    if failed:
        print(f" [RESULT] >>> FAIL <<< {len(failed)} test(s) failed: {failed}")
    else:
        print(f" [RESULT] >>> PASS <<< All {len(tests)} Feature Engineering Tests Passed!")
    print("=================================================================")


if __name__ == "__main__":
    run_tests()
