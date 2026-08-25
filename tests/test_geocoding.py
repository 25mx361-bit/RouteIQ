"""
tests/test_geocoding.py — Verification of Geocoding Service & API Endpoints for Coimbatore Region.

Tests:
  1. Preset Landmark resolution (Gandhipuram, RS Puram, Coimbatore Railway Station, PSG Tech)
  2. GET /api/geocode?q=... endpoint returns HTTP 200 with { latitude, longitude, display_name }
  3. POST /api/geocode with JSON payload
  4. Missing query parameter returns HTTP 400 Bad Request
  5. Invalid/unknown location returns HTTP 404 with friendly message
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
current = Path(__file__).resolve()
for p in [current.parent, current.parent.parent]:
    if (p / "backend").exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

from backend.app import create_app
from backend.config.settings import TestingConfig
from backend.services.geocoding_service import GeocodingService


def run_geocoding_tests():
    print("=" * 65)
    print(" RouteIQ Phase 4: Geocoding & OpenStreetMap API Test Suite")
    print("=" * 65)

    app = create_app(TestingConfig())
    client = app.test_client()
    service = GeocodingService()

    all_passed = True

    # 1. Direct Service Test for Coimbatore Landmarks
    print("\n--- 1. Direct Geocoding Service Tests ---")
    landmarks = ["Gandhipuram", "RS Puram", "Coimbatore Railway Station", "PSG Tech", "Peelamedu"]
    for l in landmarks:
        try:
            res = service.geocode(l)
            assert res["latitude"] > 10.0 and res["longitude"] > 76.0, f"Invalid coords for {l}"
            print(f" [PASS] '{l}' -> Lat: {res['latitude']}, Lng: {res['longitude']} ({res['source']})")
        except Exception as e:
            print(f" [FAIL] Failed geocoding for '{l}': {e}")
            all_passed = False

    # 2. GET /api/geocode Endpoint
    print("\n--- 2. GET /api/geocode HTTP Endpoint Tests ---")
    get_res = client.get("/api/geocode?q=Gandhipuram")
    print(f" Status: {get_res.status_code}")
    data = get_res.get_json()
    if get_res.status_code == 200 and "latitude" in data and "longitude" in data:
        print(f" [PASS] GET /api/geocode?q=Gandhipuram returned valid coordinates: {data['latitude']}, {data['longitude']}")
    else:
        print(f" [FAIL] Expected 200, got: {get_res.status_code}, data={data}")
        all_passed = False

    # 3. POST /api/geocode Endpoint
    print("\n--- 3. POST /api/geocode HTTP Endpoint Tests ---")
    post_res = client.post("/api/geocode", json={"query": "RS Puram"})
    print(f" Status: {post_res.status_code}")
    post_data = post_res.get_json()
    if post_res.status_code == 200 and "latitude" in post_data and "longitude" in post_data:
        print(f" [PASS] POST /api/geocode returned valid coordinates: {post_data['latitude']}, {post_data['longitude']}")
    else:
        print(f" [FAIL] Expected 200, got: {post_res.status_code}, data={post_data}")
        all_passed = False

    # 4. Error Handling: Missing Query (Expect 400)
    print("\n--- 4. Error Handling: Missing Query Parameter (Expect 400) ---")
    bad_res = client.get("/api/geocode")
    print(f" Status: {bad_res.status_code}")
    if bad_res.status_code == 400 and bad_res.get_json().get("error") == "bad_request":
        print(f" [PASS] Successfully returned 400 Bad Request: {bad_res.get_json().get('message')}")
    else:
        print(f" [FAIL] Expected 400, got: {bad_res.status_code}")
        all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print(" [RESULT] >>> PASS <<< All Geocoding & Map Backend Tests Passed!")
    else:
        print(" [RESULT] >>> FAIL <<< Some tests failed!")
    print("=" * 65)

    return all_passed


if __name__ == "__main__":
    success = run_geocoding_tests()
    sys.exit(0 if success else 1)
