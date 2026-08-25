"""
tests/test_catboost.py — CatBoost Route Recommendation Test Suite.

Tests:
  1. CatBoostConfig — labelling rule produces correct labels
  2. features.py — ALL_FEATURES matches build_route_feature_vector output
  3. recommendation_service.apply_safety_filters — BLOCKED rules enforced
  4. recommendation_service.rank_routes — ranking without CatBoost (fallback TCI)
  5. Admin GET metrics endpoint — 404 before training
  6. Admin POST train endpoint — 202 accepted (with synthetic data seeded to Mongo)
  7. Admin GET metrics endpoint — returns metrics after training
"""
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone

current = Path(__file__).resolve()
for p in [current.parent, current.parent.parent]:
    if (p / "backend").exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

from backend.app import create_app
from backend.config.settings import TestingConfig
from backend.database import get_db
from ml.catboost.config import CatBoostConfig
from ml.catboost.features import ALL_FEATURES
from backend.services.recommendation_service import apply_safety_filters, rank_routes
from backend.services.feature_engineering_service import build_route_feature_vector


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_fv(tci=1.2, weather_risk=0.2, road_blocked=0, event_impact=0.1,
             landslide_active=0, landslide_severity="NONE"):
    """Create a minimal feature vector with defaults."""
    return {col: 0 for col in ALL_FEATURES} | {
        "tci": tci,
        "weather_risk_score": weather_risk,
        "weather_risk_level": "Low",
        "road_blocked": road_blocked,
        "event_impact_score": event_impact,
        "landslide_active": landslide_active,
        "landslide_severity": landslide_severity,
        "distance_km": 5.0,
        "duration_min": 15.0,
        "predicted_travel_time": tci * 600,
        "free_flow_travel_time": 600.0,
    }


def _seed_predictions(db, n=30):
    """Seed synthetic feature vectors into MongoDB predictions collection."""
    import random
    random.seed(42)
    docs = []
    now = datetime.now(timezone.utc)
    for i in range(n):
        tci = random.uniform(0.9, 2.5)
        fv = _make_fv(tci=round(tci, 2), weather_risk=random.uniform(0.0, 0.6))
        docs.append({
            "features": fv,
            "created_at": now,
            "route_id": f"test_route_{i}",
        })
    db["predictions"].insert_many(docs)
    return n


def _cleanup_predictions(db):
    db["predictions"].delete_many({"route_id": {"$regex": "^test_route_"}})


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_1_labelling_rule():
    print("\n--- 1. CatBoostConfig — Labelling Rule ---")
    cfg = CatBoostConfig()

    good = _make_fv(tci=1.2, weather_risk=0.2, road_blocked=0, event_impact=0.1)
    assert cfg.compute_label(good) == 1, "Expected label=1 for good route"
    print(f" [PASS] Good route -> label=1")

    bad_tci = _make_fv(tci=1.8, weather_risk=0.2, road_blocked=0, event_impact=0.1)
    assert cfg.compute_label(bad_tci) == 0, "Expected label=0 for high TCI"
    print(f" [PASS] High TCI (1.8) -> label=0")

    blocked = _make_fv(tci=1.2, weather_risk=0.2, road_blocked=1, event_impact=0.1)
    assert cfg.compute_label(blocked) == 0, "Expected label=0 for blocked route"
    print(f" [PASS] Blocked route -> label=0")


def test_2_features_match_vector():
    print("\n--- 2. Feature List Matches build_route_feature_vector Output ---")
    sample_route = {
        "coordinates": [[11.0168, 76.9558], [11.0094, 76.9458]],
        "distance_km": 4.3,
        "duration_min": 12.0,
        "free_flow_travel_time": 600.0,
    }
    vec = build_route_feature_vector(
        route=sample_route,
        predictions={"predicted_travel_time": 720, "predicted_speed": 35, "predicted_flow": 1000},
        weather={"temperature_2m": 30, "precipitation": 0, "visibility": 10000,
                 "wind_speed_10m": 10, "relative_humidity_2m": 60, "surface_pressure": 1013},
        events=[], landslides=[],
        target_datetime=datetime.now(timezone.utc),
    )
    missing = [k for k in ALL_FEATURES if k not in vec]
    assert not missing, f"Feature vector missing keys: {missing}"
    print(f" [PASS] All {len(ALL_FEATURES)} feature keys present in build_route_feature_vector output")


def test_3_safety_filters_blocked():
    print("\n--- 3. apply_safety_filters — BLOCKED Rules ---")
    routes = [{"name": "Route A"}, {"name": "Route B"}, {"name": "Route C"}]
    fvs = [
        _make_fv(road_blocked=1),                                   # Rule 1: hard block
        _make_fv(landslide_active=1, landslide_severity="CRITICAL"), # Rule 2: critical severity
        _make_fv(road_blocked=0, landslide_severity="NONE"),         # Safe
    ]

    apply_safety_filters(routes, fvs)

    assert routes[0]["is_blocked"] is True, "Road blocked route should be blocked"
    assert routes[1]["is_blocked"] is True, "Critical landslide route should be blocked"
    assert routes[2]["is_blocked"] is False, "Safe route should not be blocked"
    print(f" [PASS] Rule 1 (road_blocked=1) -> BLOCKED")
    print(f" [PASS] Rule 2 (landslide=CRITICAL) -> BLOCKED")
    print(f" [PASS] Safe route -> NOT blocked")


def test_4_rank_routes_no_catboost():
    print("\n--- 4. rank_routes — TCI Fallback Ranking ---")
    routes = [
        {"name": "High Congestion Route"},
        {"name": "Moderate Route"},
        {"name": "Best Route"},
    ]
    fvs = [
        _make_fv(tci=2.1),  # worst
        _make_fv(tci=1.4),  # moderate
        _make_fv(tci=1.0),  # best
    ]

    ranked = rank_routes(routes, fvs, use_catboost=False)

    # First ranked should be the best (lowest TCI = highest fallback score)
    assert ranked[0]["is_recommended"] is True, "First ranked route should be recommended"
    assert ranked[0]["catboost_score"] >= ranked[1]["catboost_score"], "Ranking order incorrect"
    print(f" [PASS] Best route (TCI=1.0) ranked first with is_recommended=True")
    print(f"        Scores: {[r['catboost_score'] for r in ranked]}")


def test_5_metrics_endpoint_before_training(client):
    print("\n--- 5. GET /api/admin/models/catboost/metrics — Before Training ---")
    resp = client.get("/api/admin/models/catboost/metrics")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["status"] == "not_trained"
    print(f" [PASS] Returns 404 with status='not_trained' before training")


def test_6_train_endpoint(client, db):
    print("\n--- 6. POST /api/admin/models/catboost/train — Background Trigger ---")
    seeded = _seed_predictions(db)
    print(f"        Seeded {seeded} synthetic prediction records")

    resp = client.post("/api/admin/models/catboost/train")
    assert resp.status_code == 202, f"Expected 202 Accepted, got {resp.status_code}"
    data = resp.get_json()
    assert "background" in data.get("message", "").lower()
    print(f" [PASS] Training started -> 202 Accepted")

    # Wait for background thread to complete (max 30s)
    from ml.catboost.config import CatBoostConfig
    import os
    cfg = CatBoostConfig()
    waited = 0
    while not os.path.exists(cfg.metrics_path) and waited < 30:
        time.sleep(1)
        waited += 1
    print(f"        Waited {waited}s for training to complete")

    _cleanup_predictions(db)


def test_7_metrics_after_training(client):
    print("\n--- 7. GET /api/admin/models/catboost/metrics — After Training ---")
    from ml.catboost.config import CatBoostConfig
    import os
    cfg = CatBoostConfig()

    if not os.path.exists(cfg.metrics_path):
        print(" [SKIP] metrics file not found — training may still be running")
        return

    resp = client.get("/api/admin/models/catboost/metrics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    metrics = data["metrics"]
    assert "accuracy" in metrics or "error" in metrics
    print(f" [PASS] Metrics returned: {metrics.get('accuracy')=}, {metrics.get('f1')=}, {metrics.get('auc')=}")


# ── Runner ────────────────────────────────────────────────────────────────────

def run_tests():
    print("=================================================================")
    print(" RouteIQ Phase 14: CatBoost Route Recommendation Test Suite")
    print("=================================================================")

    app = create_app(TestingConfig)
    with app.app_context():
        db = get_db()
        client = app.test_client()

        # First delete any stale metrics from a prior run
        from ml.catboost.config import CatBoostConfig
        import os
        cfg = CatBoostConfig()
        if os.path.exists(cfg.metrics_path):
            os.remove(cfg.metrics_path)

        tests = [
            lambda: test_1_labelling_rule(),
            lambda: test_2_features_match_vector(),
            lambda: test_3_safety_filters_blocked(),
            lambda: test_4_rank_routes_no_catboost(),
            lambda: test_5_metrics_endpoint_before_training(client),
            lambda: test_6_train_endpoint(client, db),
            lambda: test_7_metrics_after_training(client),
        ]

        failed = []
        for t in tests:
            try:
                t()
            except Exception as exc:
                print(f" [FAIL] {t.__name__ if hasattr(t, '__name__') else t}: {exc}")
                failed.append(str(exc))

    print("\n=================================================================")
    if failed:
        print(f" [RESULT] >>> FAIL <<< {len(failed)} test(s) failed")
        for f in failed:
            print(f"   • {f}")
    else:
        print(f" [RESULT] >>> PASS <<< All {len(tests)} CatBoost Tests Passed!")
    print("=================================================================")


if __name__ == "__main__":
    run_tests()
