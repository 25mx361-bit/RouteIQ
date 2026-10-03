"""
tests/test_recommendation.py — RecommendationService (apply_safety_filters + rank_routes) tests.

Tests:
  1. Routes + active landslide near route → blocked route NOT recommended
  2. Routes + no landslide → highest CatBoost score is recommended
  3. All routes blocked → rank_routes returns empty or raises
  4. road_blocked flag overrides catboost score regardless
  5. LOW severity landslide does NOT block route (only HIGH/CRITICAL do)
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services.recommendation_service import apply_safety_filters, rank_routes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _route(name, catboost_score=0.80):
    return {
        "name": name,
        "distance_km": 5.0,
        "duration_min": 12.0,
        "catboost_score": catboost_score,
    }


def _fv(road_blocked=False, landslide_active=False, landslide_severity="NONE", catboost_score=0.80):
    return {
        "road_blocked": int(road_blocked),
        "landslide_active": int(landslide_active),
        "landslide_severity": landslide_severity,
        "catboost_score": catboost_score,
        "tci": 1.2,
        "weather_risk_score": 0.0,
    }


# ---------------------------------------------------------------------------
# 1. Active HIGH landslide blocks route
# ---------------------------------------------------------------------------

def test_high_landslide_blocks_route():
    routes = [_route("Route A"), _route("Route B")]
    fvs = [
        _fv(landslide_active=True, landslide_severity="HIGH", catboost_score=0.95),
        _fv(catboost_score=0.80),
    ]
    result = apply_safety_filters(routes, fvs)

    assert result[0]["is_blocked"] is True, "HIGH landslide must block the route"
    assert result[0]["catboost_eligible"] is False
    assert result[1]["is_blocked"] is False, "Safe route must NOT be blocked"
    assert result[1]["catboost_eligible"] is True


# ---------------------------------------------------------------------------
# 2. No landslide → highest CatBoost score recommended
# ---------------------------------------------------------------------------

def test_highest_catboost_score_recommended():
    routes = [
        _route("Route A", catboost_score=0.72),
        _route("Route B", catboost_score=0.91),
        _route("Route C", catboost_score=0.65),
    ]
    fvs = [
        _fv(catboost_score=0.72),
        _fv(catboost_score=0.91),
        _fv(catboost_score=0.65),
    ]
    # Apply safety (none blocked) then rank
    apply_safety_filters(routes, fvs)
    ranked = rank_routes(routes, fvs, use_catboost=False)

    # The recommended route must be "Route B" (score 0.91)
    recommended = next((r for r in ranked if r.get("is_recommended")), None)
    assert recommended is not None, "At least one route must be recommended"
    assert recommended["name"] == "Route B", (
        f"Highest CatBoost score (0.91) should be recommended, got {recommended['name']}"
    )


# ---------------------------------------------------------------------------
# 3. All routes blocked → rank_routes returns empty recommended list
# ---------------------------------------------------------------------------

def test_all_routes_blocked_returns_no_recommendation():
    routes = [_route("Route A"), _route("Route B")]
    fvs = [
        _fv(road_blocked=True),
        _fv(landslide_active=True, landslide_severity="CRITICAL"),
    ]
    apply_safety_filters(routes, fvs)
    ranked = rank_routes(routes, fvs, use_catboost=False)

    # No route should be is_recommended=True
    recommended = [r for r in ranked if r.get("is_recommended")]
    assert len(recommended) == 0, "All blocked routes must produce no recommendation"


# ---------------------------------------------------------------------------
# 4. road_blocked overrides even a very high CatBoost score
# ---------------------------------------------------------------------------

def test_road_blocked_overrides_catboost_score():
    routes = [_route("High Score Blocked", catboost_score=0.99), _route("Low Score Safe", catboost_score=0.50)]
    fvs = [
        _fv(road_blocked=True, catboost_score=0.99),
        _fv(catboost_score=0.50),
    ]
    apply_safety_filters(routes, fvs)
    ranked = rank_routes(routes, fvs, use_catboost=False)

    for r in ranked:
        if r["name"] == "High Score Blocked":
            assert r["is_blocked"] is True
            assert r.get("is_recommended") is not True, (
                "Blocked route must NEVER be recommended even with score=0.99"
            )
        if r["name"] == "Low Score Safe":
            assert r["is_blocked"] is False


# ---------------------------------------------------------------------------
# 5. LOW severity landslide does NOT block route
# ---------------------------------------------------------------------------

def test_low_severity_landslide_does_not_block():
    routes = [_route("Route A")]
    fvs = [_fv(landslide_active=True, landslide_severity="LOW", catboost_score=0.85)]
    apply_safety_filters(routes, fvs)

    assert routes[0]["is_blocked"] is False, (
        "LOW severity landslide should NOT block the route (only HIGH/CRITICAL)"
    )
    assert routes[0]["catboost_eligible"] is True


# ---------------------------------------------------------------------------
# 6. CRITICAL severity landslide blocks route
# ---------------------------------------------------------------------------

def test_critical_severity_landslide_blocks():
    routes = [_route("Critical Route")]
    fvs = [_fv(landslide_active=True, landslide_severity="CRITICAL")]
    apply_safety_filters(routes, fvs)

    assert routes[0]["is_blocked"] is True
    assert "CRITICAL" in routes[0].get("blocked_reason", "")
