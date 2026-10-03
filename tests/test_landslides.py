"""
tests/test_landslides.py — LandslideService unit tests.

Tests:
  1. Add a landslide → persisted with status REPORTED
  2. Activate landslide → status changes to ACTIVE
  3. Route passing through hazard radius → flagged BLOCKED
  4. Route far from landslide → NOT blocked
  5. Resolve landslide → status RESOLVED, no longer appears in active list
  6. Notification created when landslide is activated
"""
import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timezone
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services.landslide_service import LandslideService, _haversine_m


# ---------------------------------------------------------------------------
# Haversine helper — sanity check before service tests
# ---------------------------------------------------------------------------

def test_haversine_zero_distance():
    dist = _haversine_m(11.0168, 76.9558, 11.0168, 76.9558)
    assert dist == pytest.approx(0.0, abs=1.0), "Same point should have ~0m distance"


def test_haversine_known_distance():
    """Gandhipuram to PSG Tech (~5.1 km straight line)."""
    dist = _haversine_m(11.0168, 76.9558, 11.0244, 77.0028)
    assert 4500 < dist < 6000, f"Distance should be ~5.1km, got {dist:.0f}m"


# ---------------------------------------------------------------------------
# Fixture: LandslideService with mocked repos
# ---------------------------------------------------------------------------

@pytest.fixture()
def landslide_service():
    mock_ls_repo = MagicMock()
    mock_notif_repo = MagicMock()
    mock_sys_repo = MagicMock()
    svc = LandslideService(
        landslide_repo=mock_ls_repo,
        notif_repo=mock_notif_repo,
        sys_repo=mock_sys_repo,
    )
    return svc, mock_ls_repo, mock_notif_repo


# ---------------------------------------------------------------------------
# 1. Add a landslide
# ---------------------------------------------------------------------------

def test_add_landslide(landslide_service):
    svc, mock_repo, _ = landslide_service
    mock_repo.create.return_value = {
        "_id": "ls_001",
        "lat": 11.0500, "lng": 77.0100,
        "radius_m": 2500.0,
        "severity": "HIGH",
        "status": "REPORTED",
        "description": "Landslide on Ooty ghat road",
    }
    result = svc.add_landslide(
        lat=11.0500, lng=77.0100, radius_m=2500.0,
        severity="HIGH", description="Landslide on Ooty ghat road"
    )
    mock_repo.create.assert_called_once()
    assert result["status"] == "REPORTED"
    assert result["severity"] == "HIGH"


# ---------------------------------------------------------------------------
# 2. Activate landslide → status ACTIVE
# ---------------------------------------------------------------------------

def test_activate_landslide(landslide_service):
    svc, mock_repo, _ = landslide_service
    mock_repo.update.return_value = {"_id": "ls_001", "status": "ACTIVE", "severity": "HIGH"}
    result = svc.activate_landslide("ls_001")
    mock_repo.update.assert_called()
    assert result["status"] == "ACTIVE"


# ---------------------------------------------------------------------------
# 3. Route through hazard → BLOCKED
# ---------------------------------------------------------------------------

def test_route_near_landslide_is_blocked():
    """
    Landslide at (11.0500, 77.0100) with radius 2500m.
    Route passes exactly through that coordinate → must be BLOCKED.
    """
    svc = LandslideService.__new__(LandslideService)

    active_hazards = [{
        "lat": 11.0500,
        "lng": 77.0100,
        "radius_m": 2500.0,
        "severity": "HIGH",
        "status": "ACTIVE",
        "_id": "ls_block_test",
    }]

    # Route goes through (11.0500, 77.0100) — inside radius
    route_coords = [
        [11.0480, 77.0090],
        [11.0500, 77.0100],   # exactly at landslide
        [11.0520, 77.0110],
    ]

    result = svc.check_route_landslide_impact(route_coords, landslides=active_hazards)
    assert result["blocked"] is True, "Route through landslide must be BLOCKED"
    assert "severity" in result or "landslide_id" in result


# ---------------------------------------------------------------------------
# 4. Route far from landslide → NOT blocked
# ---------------------------------------------------------------------------

def test_route_far_from_landslide_not_blocked():
    """
    Landslide at (11.0500, 77.0100). Route is ~8km away in Gandhipuram.
    """
    svc = LandslideService.__new__(LandslideService)

    active_hazards = [{
        "lat": 11.0500,
        "lng": 77.0100,
        "radius_m": 2500.0,
        "severity": "HIGH",
        "status": "ACTIVE",
        "_id": "ls_far_test",
    }]

    # Route ~8km west of landslide
    route_coords = [
        [11.0168, 76.9558],   # Gandhipuram
        [11.0200, 76.9600],
        [11.0230, 76.9650],
    ]

    result = svc.check_route_landslide_impact(route_coords, landslides=active_hazards)
    assert result["blocked"] is False, "Route far from landslide must NOT be blocked"


# ---------------------------------------------------------------------------
# 5. Resolve landslide → no longer active
# ---------------------------------------------------------------------------

def test_resolve_landslide(landslide_service):
    svc, mock_repo, _ = landslide_service
    mock_repo.update.return_value = {"_id": "ls_001", "status": "RESOLVED"}
    mock_repo.get_active_landslides.return_value = []

    result = svc.resolve_landslide("ls_001")
    mock_repo.update.assert_called()
    assert result["status"] == "RESOLVED"

    active = svc.get_active_landslides()
    assert active == [], "Resolved landslide must not appear in active list"


# ---------------------------------------------------------------------------
# 6. Notification created on activation
# ---------------------------------------------------------------------------

def test_notification_created_on_activation(landslide_service):
    svc, mock_repo, mock_notif_repo = landslide_service
    mock_repo.update.return_value = {"_id": "ls_001", "status": "ACTIVE", "severity": "CRITICAL"}

    svc.activate_landslide("ls_001")

    # Notification repo must have been called
    assert mock_notif_repo.create.called or mock_notif_repo.add.called or mock_notif_repo.insert.called, (
        "Activating a landslide must trigger a notification"
    )
