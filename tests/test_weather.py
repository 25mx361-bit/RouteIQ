"""
tests/test_weather.py — Open-Meteo Weather API, Risk Calculator & MongoDB Storage Tests.

Tests:
  1. Weather risk calculator formula rules (rainfall, visibility, wind speed, risk levels)
  2. WeatherService.get_current_weather(lat, lng)
  3. WeatherService.get_forecast_weather(lat, lng, date, time)
  4. WeatherService.get_historical_weather(lat, lng, start_date, end_date)
  5. MongoDB persistence in weather_data collection
  6. GET /api/weather/current endpoint
  7. GET /api/weather/forecast endpoint
"""
import sys
from pathlib import Path
from datetime import datetime

# Ensure project root is in sys.path
current = Path(__file__).resolve()
for p in [current.parent, current.parent.parent]:
    if (p / "backend").exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

from backend.app import create_app
from backend.config.settings import TestingConfig
from backend.services.weather_service import WeatherService
from backend.services.weather_risk_calculator import calculate_weather_risk
from backend.repositories.weather_repository import WeatherRepository
from backend.database import get_db, init_db


def run_weather_tests():
    print("=" * 65)
    print(" RouteIQ Phase 7: Open-Meteo Weather API & Risk Calculator Test Suite")
    print("=" * 65)

    app = create_app(TestingConfig())
    client = app.test_client()
    db = get_db()
    weather_repo = WeatherRepository(db)
    service = WeatherService(weather_repo=weather_repo)

    all_passed = True

    lat, lng = 11.0168, 76.9558  # Coimbatore (Gandhipuram)

    # -----------------------------------------------------------------------
    # TEST 1: Weather Risk Calculator Formula Rules
    # -----------------------------------------------------------------------
    print("\n--- 1. Weather Risk Calculator Formula Verification ---")
    # A. Optimal Conditions
    r_optimal = calculate_weather_risk(temperature=28.0, precipitation=0.0, visibility=10000.0, wind_speed=10.0)
    assert r_optimal["risk_score"] == 0.0, f"Expected 0.0, got {r_optimal['risk_score']}"
    assert r_optimal["risk_level"] == "Low"
    print(f" [PASS] Optimal Weather: risk_score={r_optimal['risk_score']} ({r_optimal['risk_level']})")

    # B. Heavy Rainfall (>10mm -> +0.35)
    r_rain = calculate_weather_risk(precipitation=15.0)
    assert r_rain["risk_score"] >= 0.35, f"Expected >= 0.35, got {r_rain['risk_score']}"
    assert r_rain["risk_level"] == "Moderate"
    print(f" [PASS] Heavy Rain (15mm): risk_score={r_rain['risk_score']} ({r_rain['risk_level']})")

    # C. Low Visibility / Dense Fog (<1000m -> +0.30)
    r_fog = calculate_weather_risk(visibility=800.0)
    assert r_fog["risk_score"] >= 0.30, f"Expected >= 0.30, got {r_fog['risk_score']}"
    print(f" [PASS] Dense Fog (800m): risk_score={r_fog['risk_score']} ({r_fog['risk_level']})")

    # D. Severe Combined Adverse Weather
    r_severe = calculate_weather_risk(precipitation=30.0, visibility=500.0, wind_speed=55.0)
    assert r_severe["risk_score"] >= 0.75, f"Expected >= 0.75, got {r_severe['risk_score']}"
    assert r_severe["risk_level"] == "Severe"
    print(f" [PASS] Severe Weather (Rain+Fog+Gale): risk_score={r_severe['risk_score']} ({r_severe['risk_level']}) - {r_severe['risk_factors']}")

    # -----------------------------------------------------------------------
    # TEST 2: WeatherService.get_current_weather
    # -----------------------------------------------------------------------
    print("\n--- 2. WeatherService Current Weather ---")
    try:
        curr = service.get_current_weather(lat, lng, persist=True)
        assert "temperature_2m" in curr, "temperature_2m missing"
        assert "precipitation" in curr, "precipitation missing"
        assert "relative_humidity_2m" in curr, "humidity missing"
        assert "wind_speed_10m" in curr, "wind_speed missing"
        assert "weather_risk" in curr, "weather_risk missing"
        print(f" [PASS] Current Weather for Coimbatore ({lat}, {lng}):")
        print(f"   - Temp: {curr['temperature_2m']}°C | Rain: {curr['precipitation']} mm | Humidity: {curr['relative_humidity_2m']}%")
        print(f"   - Wind: {curr['wind_speed_10m']} km/h | Condition: '{curr['condition']}' | Risk: {curr['weather_risk']} ({curr['risk_level']})")
    except Exception as e:
        print(f" [FAIL] Current weather error: {e}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 3: WeatherService.get_forecast_weather
    # -----------------------------------------------------------------------
    print("\n--- 3. WeatherService Forecast Weather ---")
    try:
        fc = service.get_forecast_weather(lat, lng, date="2026-08-25", time="14:00", persist=True)
        assert "temperature_2m" in fc, "temperature_2m missing"
        assert "weather_risk" in fc, "weather_risk missing"
        print(f" [PASS] Forecast Weather for 2026-08-25 @ 14:00:")
        print(f"   - Temp: {fc['temperature_2m']}°C | Condition: '{fc['condition']}' | Risk: {fc['weather_risk']} ({fc['risk_level']})")
    except Exception as e:
        print(f" [FAIL] Forecast weather error: {e}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 4: WeatherService.get_historical_weather (Archive)
    # -----------------------------------------------------------------------
    print("\n--- 4. WeatherService Historical Weather Archive Query ---")
    try:
        hist = service.get_historical_weather(lat, lng, start_date="2024-01-01", end_date="2024-01-03")
        print(f" [PASS] Historical archive queried: retrieved {len(hist)} hourly records for ML feature set")
    except Exception as e:
        print(f" [FAIL] Historical weather archive error: {e}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 5: MongoDB weather_data Persistence Check
    # -----------------------------------------------------------------------
    print("\n--- 5. MongoDB weather_data Collection Persistence ---")
    try:
        w_doc = db.weather_data.find_one({"lat": lat, "lng": lng})
        if w_doc:
            print(f" [PASS] Record verified in MongoDB weather_data: id={w_doc['_id']}, temp={w_doc['temperature']}°C, source={w_doc['source']}")
        else:
            print(f" [FAIL] Weather record not found in MongoDB")
            all_passed = False
    except Exception as e:
        print(f" [FAIL] MongoDB check error: {e}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 6: GET /api/weather/current Endpoint
    # -----------------------------------------------------------------------
    print("\n--- 6. GET /api/weather/current Endpoint ---")
    res_curr = client.get(f"/api/weather/current?lat={lat}&lng={lng}")
    print(f" Status: {res_curr.status_code}")
    data_curr = res_curr.get_json()
    if res_curr.status_code == 200 and "temperature_2m" in data_curr and "weather_risk" in data_curr:
        print(f" [PASS] Current weather endpoint working: {data_curr['temperature_2m']}°C, {data_curr['condition']}, Risk={data_curr['weather_risk']}")
    else:
        print(f" [FAIL] Expected 200, got: {res_curr.status_code}, data={data_curr}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 7: GET /api/weather/forecast Endpoint
    # -----------------------------------------------------------------------
    print("\n--- 7. GET /api/weather/forecast Endpoint ---")
    res_fc = client.get(f"/api/weather/forecast?lat={lat}&lng={lng}&date=2026-08-25&time=18:00")
    print(f" Status: {res_fc.status_code}")
    data_fc = res_fc.get_json()
    if res_fc.status_code == 200 and "temperature_2m" in data_fc and "weather_risk" in data_fc:
        print(f" [PASS] Forecast weather endpoint working: {data_fc['temperature_2m']}°C, {data_fc['condition']}, Risk={data_fc['weather_risk']}")
    else:
        print(f" [FAIL] Expected 200, got: {res_fc.status_code}, data={data_fc}")
        all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print(" [RESULT] >>> PASS <<< All Open-Meteo Weather & Risk Tests Passed!")
    else:
        print(" [RESULT] >>> FAIL <<< Some weather tests failed!")
    print("=" * 65)

    return all_passed


if __name__ == "__main__":
    success = run_weather_tests()
    sys.exit(0 if success else 1)
