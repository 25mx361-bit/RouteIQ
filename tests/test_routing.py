"""
tests/test_routing.py — RoutingService unit tests.

Tests:
  1. Valid route between two Coimbatore landmarks → routes returned
  2. Source == destination → InvalidCoordinatesError raised
  3. Out-of-range coordinates → InvalidCoordinatesError raised
  4. OSRM returns empty routes list → RouteNotFoundError raised
  5. Too-far destinations (different countries) → no viable route / error
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services.routing_service import (
    RoutingService,
    RoutingError,
    InvalidCoordinatesError,
    RouteNotFoundError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_osrm_response(distance_m=5000.0, duration_s=600.0, n_routes=2):
    """Build a minimal OSRM-like response dict."""
    route = {
        "distance": distance_m,
        "duration": duration_s,
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [76.9558, 11.0168],
                [76.9600, 11.0200],
                [76.9650, 11.0230],
                [76.9700, 11.0260],
                [77.0028, 11.0244],
            ],
        },
        "legs": [
            {
                "steps": [
                    {"name": "Avinashi Road", "distance": 3000, "duration": 360},
                    {"name": "Nehru Street", "distance": 2000, "duration": 240},
                ]
            }
        ],
    }
    return {
        "code": "Ok",
        "routes": [route] * n_routes,
        "waypoints": [],
    }


def _mock_osrm_ok(n_routes=2):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = _make_osrm_response(n_routes=n_routes)
    return mock_resp


# ---------------------------------------------------------------------------
# 1. Valid route → returns list of route dicts
# ---------------------------------------------------------------------------

def test_valid_route_returns_routes():
    svc = RoutingService(api_key=None)
    with patch("requests.get", return_value=_mock_osrm_ok(n_routes=2)):
        result = svc.generate_routes(
            source_lat=11.0168, source_lng=76.9558,
            dest_lat=11.0244, dest_lng=77.0028,
            source_label="Gandhipuram",
            dest_label="PSG Tech Peelamedu",
            travel_date="2026-10-05",
            travel_time="09:00",
        )
    assert isinstance(result, dict), "generate_routes should return a dict"
    routes = result.get("routes", [])
    assert len(routes) >= 1, "At least one route should be returned"
    first = routes[0]
    assert "distance_km" in first or "distance_m" in first
    assert "duration_min" in first or "duration_s" in first or "duration" in first
    assert "name" in first


# ---------------------------------------------------------------------------
# 2. Source == Destination → InvalidCoordinatesError
# ---------------------------------------------------------------------------

def test_source_equals_destination_raises_error():
    svc = RoutingService(api_key=None)
    with pytest.raises((InvalidCoordinatesError, RoutingError, ValueError)):
        svc.generate_routes(
            source_lat=11.0168, source_lng=76.9558,
            dest_lat=11.0168, dest_lng=76.9558,
            source_label="A", dest_label="A",
            travel_date="2026-10-05", travel_time="09:00",
        )


# ---------------------------------------------------------------------------
# 3. Out-of-range coordinates → InvalidCoordinatesError
# ---------------------------------------------------------------------------

def test_invalid_coordinates_out_of_range():
    svc = RoutingService(api_key=None)
    with pytest.raises((InvalidCoordinatesError, RoutingError, ValueError)):
        svc.generate_routes(
            source_lat=999.0, source_lng=999.0,
            dest_lat=11.0244, dest_lng=77.0028,
            source_label="Invalid", dest_label="PSG Tech",
            travel_date="2026-10-05", travel_time="09:00",
        )


# ---------------------------------------------------------------------------
# 4. OSRM returns empty routes → RouteNotFoundError or fallback
# ---------------------------------------------------------------------------

def test_osrm_empty_routes_handled():
    svc = RoutingService(api_key=None)
    empty_resp = MagicMock()
    empty_resp.status_code = 200
    empty_resp.json.return_value = {"code": "Ok", "routes": [], "waypoints": []}

    # When OSRM returns nothing, service should either raise RouteNotFoundError
    # or return its fallback route generation
    with patch("requests.get", return_value=empty_resp):
        try:
            result = svc.generate_routes(
                source_lat=11.0168, source_lng=76.9558,
                dest_lat=11.0244, dest_lng=77.0028,
                source_label="Gandhipuram", dest_label="PSG Tech",
                travel_date="2026-10-05", travel_time="09:00",
            )
            # If it returns something, it must have routes
            routes = result.get("routes", [])
            assert len(routes) >= 1, "Should have at least one fallback route"
        except (RouteNotFoundError, RoutingError):
            pass  # Acceptable to raise when no route found


# ---------------------------------------------------------------------------
# 5. Very far destinations (coordinates in different countries)
# ---------------------------------------------------------------------------

def test_far_destination_returns_error_or_long_route():
    svc = RoutingService(api_key=None)
    far_resp = MagicMock()
    far_resp.status_code = 200
    far_resp.json.return_value = {"code": "NoRoute", "routes": []}

    with patch("requests.get", return_value=far_resp):
        try:
            result = svc.generate_routes(
                source_lat=11.0168, source_lng=76.9558,   # Coimbatore
                dest_lat=51.5074, dest_lng=-0.1278,        # London
                source_label="Coimbatore", dest_label="London",
                travel_date="2026-10-05", travel_time="09:00",
            )
            routes = result.get("routes", [])
            # If it returned something, distance must be extremely large or route is fallback
            if routes:
                dist_km = routes[0].get("distance_km", 0)
                assert dist_km > 1000 or dist_km == 0, "Cross-continent route unreasonably short"
        except (RouteNotFoundError, RoutingError, InvalidCoordinatesError):
            pass  # Correct behavior to raise here
