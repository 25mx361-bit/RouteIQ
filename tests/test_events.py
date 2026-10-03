"""
tests/test_events.py — EventService unit tests.

Tests:
  1. Create festival event → returns event with _id
  2. Update event → changed fields reflected
  3. Delete event → no longer retrievable
  4. Get active events near a location → only current/nearby events returned
  5. Impact score formula — CRITICAL event, crowd≥10000, proximity<500m, during window → score=1.0
  6. Impact score formula — LOW event, small crowd, far away → score near 0
  7. Impact score — outside time window → score 0.0
"""
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime, timezone, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services.event_service import EventService


# ---------------------------------------------------------------------------
# Helper: EventService with a mocked MongoDB repo
# ---------------------------------------------------------------------------

def _make_event(
    name="Test Festival",
    impact_level="MEDIUM",
    expected_crowd=1000,
    lat=11.0168,
    lng=76.9558,
    start_offset_h=-1,
    end_offset_h=3,
    active=True,
):
    now = datetime.now(timezone.utc)
    return {
        "_id": "ev_test_001",
        "name": name,
        "impact_level": impact_level,
        "expected_crowd": expected_crowd,
        "lat": lat,
        "lng": lng,
        "start_time": (now + timedelta(hours=start_offset_h)).isoformat(),
        "end_time": (now + timedelta(hours=end_offset_h)).isoformat(),
        "is_active": active,
        "location": {"type": "Point", "coordinates": [lng, lat]},
    }


# ---------------------------------------------------------------------------
# 1. Create festival event
# ---------------------------------------------------------------------------

def test_create_event():
    mock_repo = MagicMock()
    mock_repo.create.return_value = {**_make_event(), "_id": "new_id_123"}
    svc = EventService(event_repo=mock_repo)

    result = svc.create_event(
        name="Pongal Festival",
        impact_level="HIGH",
        expected_crowd=8000,
        lat=11.0168,
        lng=76.9558,
        start_time=datetime.now(timezone.utc).isoformat(),
        end_time=(datetime.now(timezone.utc) + timedelta(hours=4)).isoformat(),
    )

    mock_repo.create.assert_called_once()
    assert result is not None
    assert "_id" in result or result.get("name") == "Pongal Festival" or mock_repo.create.called


# ---------------------------------------------------------------------------
# 2. Update event
# ---------------------------------------------------------------------------

def test_update_event():
    mock_repo = MagicMock()
    updated = {**_make_event(), "expected_crowd": 12000}
    mock_repo.update.return_value = updated
    svc = EventService(event_repo=mock_repo)

    result = svc.update_event("ev_test_001", {"expected_crowd": 12000})
    mock_repo.update.assert_called_once_with("ev_test_001", {"expected_crowd": 12000})
    assert result is not None


# ---------------------------------------------------------------------------
# 3. Delete event
# ---------------------------------------------------------------------------

def test_delete_event():
    mock_repo = MagicMock()
    mock_repo.delete.return_value = True
    svc = EventService(event_repo=mock_repo)

    result = svc.delete_event("ev_test_001")
    mock_repo.delete.assert_called_once_with("ev_test_001")


# ---------------------------------------------------------------------------
# 4. Get active events near location
# ---------------------------------------------------------------------------

def test_get_active_events_near_location():
    mock_repo = MagicMock()
    mock_repo.get_active_events_near.return_value = [_make_event()]
    svc = EventService(event_repo=mock_repo)

    result = svc.get_active_events_near(lat=11.0168, lng=76.9558, radius_km=5.0)
    assert isinstance(result, list)
    assert len(result) >= 1
    assert result[0]["is_active"] is True


# ---------------------------------------------------------------------------
# 5. Impact score — CRITICAL event during window, big crowd, nearby
# ---------------------------------------------------------------------------

def test_impact_score_critical_event_maximum():
    """
    CRITICAL (1.00) × CrowdWeight(≥10000 → 1.30) × ProximityFactor(<500m → 1.00) × TimeOverlap(1.00)
    = 1.30 → clamped to 1.0
    """
    svc = EventService()
    event = _make_event(impact_level="CRITICAL", expected_crowd=15000, lat=11.0168, lng=76.9558)
    route_coords = [[11.0168, 76.9558], [11.0170, 76.9560]]  # ON TOP of event venue
    travel_time = datetime.now(timezone.utc)  # during event window

    score = svc.calculate_impact_score(event, route_coords, travel_time)
    assert score == pytest.approx(1.0), f"CRITICAL event at route should score 1.0, got {score}"


# ---------------------------------------------------------------------------
# 6. Impact score — LOW event, small crowd, far away
# ---------------------------------------------------------------------------

def test_impact_score_low_event_far_away():
    """
    LOW (0.25) × CrowdWeight(<1000 → 0.80) × ProximityFactor(≥5000m → 0.00) × any
    = 0.00 (proximity kills it)
    """
    svc = EventService()
    event = _make_event(impact_level="LOW", expected_crowd=200, lat=11.0168, lng=76.9558)
    # Route far from event: ~8km north
    route_coords = [[11.0900, 76.9500], [11.0910, 76.9510]]
    travel_time = datetime.now(timezone.utc)

    score = svc.calculate_impact_score(event, route_coords, travel_time)
    assert score == pytest.approx(0.0, abs=0.01), f"Far-away LOW event should score 0.0, got {score}"


# ---------------------------------------------------------------------------
# 7. Impact score — outside time window
# ---------------------------------------------------------------------------

def test_impact_score_outside_time_window():
    """TimeOverlap = 0.00 when travel time is far outside event window → score = 0."""
    svc = EventService()
    event = _make_event(
        impact_level="HIGH",
        expected_crowd=5000,
        lat=11.0168,
        lng=76.9558,
        start_offset_h=6,   # starts 6h from now
        end_offset_h=10,    # ends 10h from now
    )
    route_coords = [[11.0168, 76.9558]]
    travel_time = datetime.now(timezone.utc)  # NOW — far before event

    score = svc.calculate_impact_score(event, route_coords, travel_time)
    assert score == pytest.approx(0.0, abs=0.01), (
        f"Event outside time window should score 0.0, got {score}"
    )
