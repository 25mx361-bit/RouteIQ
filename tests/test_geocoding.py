"""
tests/test_geocoding.py — GeocodingService unit tests.

Tests:
  1. Valid Coimbatore landmark → returns preset coordinates immediately
  2. Valid location string (Nominatim) → lat/lng/display_name returned
  3. Empty string → raises or returns None gracefully
  4. Special characters in query → handled without exception
  5. Unknown location (far away) → Nominatim fallback attempted
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services.geocoding_service import GeocodingService, COIMBATORE_PRESETS


# ---------------------------------------------------------------------------
# 1. Valid Coimbatore preset (instant lookup — no HTTP call needed)
# ---------------------------------------------------------------------------

def test_geocode_coimbatore_preset_gandhipuram():
    svc = GeocodingService()
    result = svc.geocode("gandhipuram")
    assert result is not None, "Should return preset result for gandhipuram"
    assert abs(result["latitude"] - 11.0176) < 0.01
    assert abs(result["longitude"] - 76.9667) < 0.01
    assert "Gandhipuram" in result["display_name"]


def test_geocode_coimbatore_preset_rs_puram():
    svc = GeocodingService()
    result = svc.geocode("rs puram")
    assert result is not None
    assert abs(result["latitude"] - 11.0085) < 0.01


def test_geocode_coimbatore_preset_case_insensitive():
    svc = GeocodingService()
    result = svc.geocode("GANDHIPURAM")
    assert result is not None
    assert "latitude" in result and "longitude" in result


# ---------------------------------------------------------------------------
# 2. Valid location → Nominatim response parsed correctly
# ---------------------------------------------------------------------------

def test_geocode_valid_location_via_nominatim():
    """Mocks Nominatim and verifies correct field mapping."""
    svc = GeocodingService()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "lat": "11.0168",
            "lon": "76.9558",
            "display_name": "Saravanampatti, Coimbatore, Tamil Nadu, India",
        }
    ]
    with patch("requests.get", return_value=mock_response):
        result = svc.geocode("Saravanampatti Coimbatore")
    assert result is not None
    assert abs(float(result["latitude"]) - 11.0168) < 0.001
    assert abs(float(result["longitude"]) - 76.9558) < 0.001
    assert "display_name" in result


# ---------------------------------------------------------------------------
# 3. Empty string → returns None or raises cleanly
# ---------------------------------------------------------------------------

def test_geocode_empty_string():
    svc = GeocodingService()
    # Should not raise an unhandled exception — returns None or raises ValueError
    try:
        result = svc.geocode("")
        assert result is None, "Empty string should return None, not a result"
    except (ValueError, TypeError):
        pass  # Also acceptable to raise a validation error


# ---------------------------------------------------------------------------
# 4. Special characters → handled without crash
# ---------------------------------------------------------------------------

def test_geocode_special_characters():
    svc = GeocodingService()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    with patch("requests.get", return_value=mock_response):
        try:
            result = svc.geocode("!@#$%^&*()")
            # Returns None when Nominatim finds nothing — acceptable
            assert result is None or "latitude" in result
        except Exception as e:
            pytest.fail(f"Special characters should not cause unhandled exception: {e}")


# ---------------------------------------------------------------------------
# 5. Nominatim returns empty list (unknown location)
# ---------------------------------------------------------------------------

def test_geocode_unknown_location_returns_none():
    svc = GeocodingService()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    with patch("requests.get", return_value=mock_response):
        result = svc.geocode("xyzzy_nonexistent_place_12345")
    assert result is None, "Unknown location should return None"


# ---------------------------------------------------------------------------
# 6. Nominatim HTTP error → graceful fallback (no exception propagated)
# ---------------------------------------------------------------------------

def test_geocode_network_error_handled_gracefully():
    svc = GeocodingService()
    import requests as req_mod
    with patch("requests.get", side_effect=req_mod.exceptions.ConnectionError("timeout")):
        try:
            result = svc.geocode("Some Place Coimbatore")
            # Should return None or preset, not raise
            assert result is None or "latitude" in result
        except Exception as e:
            pytest.fail(f"Network error should be handled gracefully, got: {e}")
