"""
tests/test_weather.py — WeatherService unit tests.

Tests:
  1. Current weather → dict with required fields (temperature, rainfall_mm, etc.)
  2. Forecast for future time → returns hourly forecast dict
  3. Historical weather fetch → list of records for date range
  4. WeatherRiskCalculator — sunny day → risk_score near 0, risk_level "Low"
  5. WeatherRiskCalculator — torrential rain (>25mm) → score ≥ 0.50
  6. WeatherRiskCalculator — heavy rain + low visibility + gale wind → score = 1.0 (capped)
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services.weather_risk_calculator import calculate_weather_risk


# ---------------------------------------------------------------------------
# Open-Meteo mock payloads
# ---------------------------------------------------------------------------

CURRENT_MOCK = {
    "current": {
        "temperature_2m": 31.5,
        "precipitation": 0.0,
        "visibility": 10000.0,
        "windspeed_10m": 12.0,
        "relativehumidity_2m": 68.0,
        "weathercode": 1,
    },
    "current_units": {
        "temperature_2m": "°C",
        "precipitation": "mm",
        "windspeed_10m": "km/h",
        "visibility": "m",
    }
}

FORECAST_MOCK = {
    "hourly": {
        "time": ["2026-10-05T09:00", "2026-10-05T10:00"],
        "temperature_2m": [28.0, 29.5],
        "precipitation": [0.0, 0.2],
        "visibility": [10000.0, 9000.0],
        "windspeed_10m": [8.0, 10.0],
        "relativehumidity_2m": [65.0, 67.0],
        "weathercode": [1, 2],
    }
}

HISTORICAL_MOCK = {
    "hourly": {
        "time": ["2026-09-01T00:00", "2026-09-01T01:00"],
        "temperature_2m": [26.0, 25.5],
        "precipitation": [0.5, 1.2],
        "windspeed_10m": [9.0, 11.0],
        "relativehumidity_2m": [72.0, 74.0],
        "visibility": [9000.0, 8500.0],
        "weathercode": [61, 61],
    }
}


def _mock_open_meteo(payload):
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = payload
    return m


# ---------------------------------------------------------------------------
# 1. Current weather → required fields present
# ---------------------------------------------------------------------------

def test_current_weather_returns_required_fields():
    with patch("requests.get", return_value=_mock_open_meteo(CURRENT_MOCK)):
        from backend.services.weather_service import WeatherService
        svc = WeatherService()
        result = svc.get_current_weather(lat=11.0168, lng=76.9558)

    assert result is not None
    assert "temperature" in result
    assert "rainfall_mm" in result or "precipitation" in result
    assert "wind_speed" in result or "windspeed" in result
    assert "condition" in result or "weather_code" in result or "weathercode" in result


# ---------------------------------------------------------------------------
# 2. Forecast for future time → returns hourly data
# ---------------------------------------------------------------------------

def test_forecast_weather_returns_hourly_data():
    with patch("requests.get", return_value=_mock_open_meteo(FORECAST_MOCK)):
        from backend.services.weather_service import WeatherService
        svc = WeatherService()
        result = svc.get_forecast_weather(
            lat=11.0168, lng=76.9558,
            date="2026-10-05", time="09:00"
        )

    assert result is not None
    # Should return a forecast dict or list with at least temperature
    if isinstance(result, list):
        assert len(result) >= 1
        assert "temperature" in result[0] or "temperature_2m" in result[0]
    else:
        assert "temperature" in result or "temperature_2m" in result


# ---------------------------------------------------------------------------
# 3. Historical weather → list of records
# ---------------------------------------------------------------------------

def test_historical_weather_returns_records():
    with patch("requests.get", return_value=_mock_open_meteo(HISTORICAL_MOCK)):
        from backend.services.weather_service import WeatherService
        svc = WeatherService()
        result = svc.get_historical_weather(
            lat=11.0168, lng=76.9558,
            start_date="2026-09-01", end_date="2026-09-02"
        )

    assert result is not None
    if isinstance(result, list):
        assert len(result) >= 1
    else:
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# 4. Sunny day → Low risk, score near 0
# ---------------------------------------------------------------------------

def test_weather_risk_sunny_day():
    result = calculate_weather_risk(
        temperature=28.0,
        precipitation=0.0,
        visibility=10000.0,
        wind_speed=10.0,
    )
    assert result["risk_score"] == 0.0, f"Sunny day should have risk_score=0.0, got {result['risk_score']}"
    assert result["risk_level"] == "Low"
    assert result["is_hazardous"] is False


# ---------------------------------------------------------------------------
# 5. Torrential rain (>25mm) → score ≥ 0.50
# ---------------------------------------------------------------------------

def test_weather_risk_torrential_rain():
    result = calculate_weather_risk(
        temperature=26.0,
        precipitation=30.0,   # > 25mm → +0.50
        visibility=10000.0,
        wind_speed=10.0,
    )
    assert result["risk_score"] >= 0.50, (
        f"Torrential rain should give risk_score >= 0.50, got {result['risk_score']}"
    )
    assert "Torrential" in " ".join(result.get("risk_factors", [])) or result["risk_score"] >= 0.50


# ---------------------------------------------------------------------------
# 6. Combined worst-case → score capped at 1.0
# ---------------------------------------------------------------------------

def test_weather_risk_combined_worst_case_capped_at_1():
    result = calculate_weather_risk(
        temperature=28.0,
        precipitation=35.0,    # +0.50
        visibility=500.0,      # +0.30
        wind_speed=60.0,       # +0.25
    )
    assert result["risk_score"] == 1.0, (
        f"Worst-case weather should clamp risk_score to 1.0, got {result['risk_score']}"
    )
    assert result["risk_level"] == "Severe"
    assert result["is_hazardous"] is True


# ---------------------------------------------------------------------------
# 7. Moderate rain (2.5–10mm) → score 0.20 contribution
# ---------------------------------------------------------------------------

def test_weather_risk_moderate_rain_boundary():
    result = calculate_weather_risk(
        temperature=28.0,
        precipitation=5.0,    # 2.5 < 5 <= 10 → +0.20
        visibility=10000.0,
        wind_speed=10.0,
    )
    assert result["risk_score"] == pytest.approx(0.20, abs=0.01), (
        f"Moderate rain (5mm) should contribute +0.20, got {result['risk_score']}"
    )


# ---------------------------------------------------------------------------
# 8. Extreme temperature → +0.10 contribution
# ---------------------------------------------------------------------------

def test_weather_risk_extreme_temperature():
    result_hot = calculate_weather_risk(temperature=45.0, precipitation=0.0, visibility=10000.0, wind_speed=10.0)
    result_cold = calculate_weather_risk(temperature=0.0, precipitation=0.0, visibility=10000.0, wind_speed=10.0)
    assert result_hot["risk_score"] == pytest.approx(0.10, abs=0.01), "Extreme heat should add +0.10"
    assert result_cold["risk_score"] == pytest.approx(0.10, abs=0.01), "Frost should add +0.10"
