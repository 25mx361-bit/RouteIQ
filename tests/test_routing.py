"""
tests/test_routing.py — OpenRouteService & Route Alternatives Backend Tests.

Tests:
  1. RoutingService generates at least 3 alternative routes
  2. GET /api/routes/search with query parameters returns 200 and routes
  3. POST /api/routes/search with JSON payload returns 200 and routes
  4. Routes are stored in MongoDB with valid search_id
  5. GET /api/routes/alternatives?search_id= retrieves the saved routes
  6. Invalid coordinates correctly rejected with HTTP 422
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
from backend.services.routing_service import RoutingService
from backend.repositories.route_repository import RouteRepository


def run_routing_tests():
    print("=" * 65)
    print(" RouteIQ Phase 5: Routing & Alternatives Test Suite")
    print("=" * 65)

    app = create_app(TestingConfig())
    client = app.test_client()
    service = RoutingService()

    all_passed = True

    # Coimbatore Coordinates: Gandhipuram -> RS Puram
    s_lat, s_lng = 11.0168, 76.9558
    d_lat, d_lng = 11.0094, 76.9458

    # -----------------------------------------------------------------------
    # TEST 1: Routing Service Direct Call
    # -----------------------------------------------------------------------
    print("\n--- 1. Direct RoutingService Generation ---")
    try:
        res = service.generate_routes(
            source_lat=s_lat,
            source_lng=s_lng,
            dest_lat=d_lat,
            dest_lng=d_lng,
            source_label="Gandhipuram",
            dest_label="RS Puram",
        )
        assert "search_id" in res, "No search_id returned"
        assert res["routes_count"] >= 3, f"Expected at least 3 routes, got {res['routes_count']}"
        print(f" [PASS] Generated {res['routes_count']} alternative routes, search_id={res['search_id']}")
        for idx, r in enumerate(res["routes"]):
            print(f"   - Route {idx + 1}: '{r['name']}' | {r['distance_km']} km | {r['duration_min']} mins ({len(r['coordinates'])} points)")
        search_id = res["search_id"]
    except Exception as e:
        print(f" [FAIL] RoutingService error: {e}")
        all_passed = False
        search_id = None

    # -----------------------------------------------------------------------
    # TEST 2: GET /api/routes/search Endpoint
    # -----------------------------------------------------------------------
    print("\n--- 2. GET /api/routes/search Endpoint ---")
    params = {
        "source_lat": s_lat,
        "source_lng": s_lng,
        "dest_lat": d_lat,
        "dest_lng": d_lng,
        "source_label": "Gandhipuram",
        "dest_label": "RS Puram",
        "date": "2026-08-25",
        "time": "09:30",
    }
    get_res = client.get("/api/routes/search", query_string=params)
    print(f" Status: {get_res.status_code}")
    data = get_res.get_json()
    if get_res.status_code == 200 and data.get("routes_count", 0) >= 3:
        print(f" [PASS] GET route search returned {data['routes_count']} routes with search_id={data['search_id']}")
    else:
        print(f" [FAIL] Expected 200 with >=3 routes, got: {get_res.status_code}, data={data}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 3: POST /api/routes/search Endpoint
    # -----------------------------------------------------------------------
    print("\n--- 3. POST /api/routes/search Endpoint ---")
    post_res = client.post("/api/routes/search", json=params)
    print(f" Status: {post_res.status_code}")
    post_data = post_res.get_json()
    if post_res.status_code == 200 and post_data.get("routes_count", 0) >= 3:
        print(f" [PASS] POST route search returned {post_data['routes_count']} routes")
    else:
        print(f" [FAIL] Expected 200 with >=3 routes, got: {post_res.status_code}, data={post_data}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 4: GET /api/routes/alternatives by search_id
    # -----------------------------------------------------------------------
    print("\n--- 4. GET /api/routes/alternatives by search_id ---")
    if search_id:
        alt_res = client.get(f"/api/routes/alternatives?search_id={search_id}")
        print(f" Status: {alt_res.status_code}")
        alt_data = alt_res.get_json()
        if alt_res.status_code == 200 and alt_data.get("routes_count", 0) >= 3:
            print(f" [PASS] Retrieved {alt_data['routes_count']} saved routes from MongoDB for {search_id}")
        else:
            print(f" [FAIL] Expected 200, got: {alt_res.status_code}, data={alt_data}")
            all_passed = False

    # -----------------------------------------------------------------------
    # TEST 5: Invalid Coordinates (Expect 422)
    # -----------------------------------------------------------------------
    print("\n--- 5. Invalid Coordinates Validation (Expect 422) ---")
    bad_params = {
        "source_lat": 999.0,  # Invalid latitude
        "source_lng": 76.9558,
        "dest_lat": 11.0094,
        "dest_lng": 76.9458,
    }
    bad_res = client.get("/api/routes/search", query_string=bad_params)
    print(f" Status: {bad_res.status_code}")
    if bad_res.status_code == 422:
        print(f" [PASS] Successfully caught invalid coordinates with 422: {bad_res.get_json().get('message')}")
    else:
        print(f" [FAIL] Expected 422, got: {bad_res.status_code}")
        all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print(" [RESULT] >>> PASS <<< All Routing & Alternatives Tests Passed!")
    else:
        print(" [RESULT] >>> FAIL <<< Some tests failed!")
    print("=" * 65)

    return all_passed


if __name__ == "__main__":
    success = run_routing_tests()
    sys.exit(0 if success else 1)
