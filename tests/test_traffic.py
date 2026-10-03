"""
tests/test_traffic.py — TrafficService & TrafficAdapter unit tests.

Tests:
  1. TomTom mock response → all expected fields parsed correctly
  2. SimulatedTrafficAdapter → always returns a valid response structure
  3. TrafficService in-memory cache → second call within TTL returns cached data
  4. Cache expiry → after TTL, a fresh API call is made
  5. TomTom API key missing → graceful fallback to SimulatedTrafficAdapter
"""
import pytest
import time
from unittest.mock import patch, MagicMock, call
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services.traffic_adapter import (
    TomTomTrafficAdapter,
    SimulatedTrafficAdapter,
)
from backend.services.traffic_service import TrafficService


# ---------------------------------------------------------------------------
# Minimal valid TomTom Flow Segment API response
# ---------------------------------------------------------------------------

TOMTOM_MOCK_PAYLOAD = {
    "flowSegmentData": {
        "frc": "FRC3",
        "currentSpeed": 38,
        "freeFlowSpeed": 52,
        "currentTravelTime": 78,
        "freeFlowTravelTime": 57,
        "confidence": 0.87,
        "roadClosure": False,
    }
}


# ---------------------------------------------------------------------------
# 1. TomTom adapter → fields parsed correctly
# ---------------------------------------------------------------------------

def test_tomtom_adapter_parses_response_correctly():
    adapter = TomTomTrafficAdapter(api_key="fake-test-key-1234")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = TOMTOM_MOCK_PAYLOAD

    with patch("requests.get", return_value=mock_resp):
        result = adapter.get_flow_segment(lat=11.0168, lng=76.9558, zoom=10)

    assert result is not None, "TomTom adapter should return a parsed result"
    assert "current_speed" in result or "currentSpeed" in result or "speed_kmh" in result
    assert "free_flow_speed" in result or "freeFlowSpeed" in result or "free_flow_speed_kmh" in result

    # Extract whatever field mapping the adapter uses
    speed = result.get("current_speed") or result.get("currentSpeed") or result.get("speed_kmh") or 0
    ff_speed = result.get("free_flow_speed") or result.get("freeFlowSpeed") or result.get("free_flow_speed_kmh") or 0

    assert speed == 38, f"Current speed should be 38, got {speed}"
    assert ff_speed == 52, f"Free flow speed should be 52, got {ff_speed}"


# ---------------------------------------------------------------------------
# 2. SimulatedTrafficAdapter → always returns valid structure
# ---------------------------------------------------------------------------

def test_simulated_adapter_returns_valid_structure():
    adapter = SimulatedTrafficAdapter()
    result = adapter.get_flow_segment(lat=11.0168, lng=76.9558, zoom=10)
    assert result is not None, "Simulated adapter must always return a result"
    assert isinstance(result, dict)
    # Must have at minimum a speed-like field
    has_speed = any(k in result for k in ("speed_kmh", "current_speed", "currentSpeed", "predicted_speed_kmh"))
    assert has_speed, f"Simulated result missing speed field: {result.keys()}"


# ---------------------------------------------------------------------------
# 3. TrafficService cache — second call within TTL uses cache
# ---------------------------------------------------------------------------

def test_traffic_service_cache_hit():
    """Within TTL, get_flow_at_point should not call the provider again."""
    adapter = SimulatedTrafficAdapter()
    call_count = {"n": 0}
    original_get = adapter.get_flow_segment

    def counting_get(lat, lng, zoom=10):
        call_count["n"] += 1
        return original_get(lat, lng, zoom)

    adapter.get_flow_segment = counting_get

    svc = TrafficService(provider=adapter, cache_ttl_sec=60)

    # First call — must hit provider
    svc.get_flow_at_point(11.0168, 76.9558, persist=False)
    assert call_count["n"] == 1, "First call should hit the provider"

    # Second call immediately — should use cache
    svc.get_flow_at_point(11.0168, 76.9558, persist=False)
    assert call_count["n"] == 1, "Second call within TTL should use cache, not hit provider again"


# ---------------------------------------------------------------------------
# 4. Cache expiry — after TTL, provider is called again
# ---------------------------------------------------------------------------

def test_traffic_service_cache_miss_after_expiry():
    adapter = SimulatedTrafficAdapter()
    call_count = {"n": 0}
    original_get = adapter.get_flow_segment

    def counting_get(lat, lng, zoom=10):
        call_count["n"] += 1
        return original_get(lat, lng, zoom)

    adapter.get_flow_segment = counting_get

    svc = TrafficService(provider=adapter, cache_ttl_sec=0)  # 0-second TTL = always expired

    svc.get_flow_at_point(11.0168, 76.9558, persist=False)
    svc.get_flow_at_point(11.0168, 76.9558, persist=False)

    assert call_count["n"] == 2, "Both calls should hit the provider when TTL=0"


# ---------------------------------------------------------------------------
# 5. Missing TomTom API key → falls back to simulated
# ---------------------------------------------------------------------------

def test_traffic_service_fallback_when_no_api_key():
    """TomTomAdapter without a key should return None so TrafficService uses fallback."""
    adapter = TomTomTrafficAdapter(api_key="")
    result = adapter.get_flow_segment(lat=11.0168, lng=76.9558, zoom=10)
    # Should return None (no key → no API call)
    assert result is None, "TomTom adapter without API key should return None"

    # TrafficService wraps it — should still return a result via fallback
    svc = TrafficService(provider=adapter)
    flow = svc.get_flow_at_point(11.0168, 76.9558, persist=False)
    assert flow is not None, "TrafficService should return result via fallback even without TomTom key"
