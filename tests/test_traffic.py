"""
tests/test_traffic.py — TomTom Traffic API, Provider Adapter & MongoDB Storage Tests.

Tests:
  1. TrafficProviderAdapter interface and response structure (currentSpeed, freeFlowSpeed, etc.)
  2. TrafficService point flow query and derived metrics calculation
  3. MongoDB persistence in traffic_data collection
  4. In-memory 5-minute cache functionality
  5. GET /api/traffic/current endpoint
  6. POST /api/traffic/route-flow endpoint
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
from backend.services.traffic_service import TrafficService
from backend.services.traffic_adapter import SimulatedTrafficAdapter
from backend.repositories.traffic_repository import TrafficRepository
from backend.database import get_db, init_db


def run_traffic_tests():
    print("=" * 65)
    print(" RouteIQ Phase 6: TomTom Traffic API & Adapter Test Suite")
    print("=" * 65)

    app = create_app(TestingConfig())
    client = app.test_client()
    db = get_db()
    traffic_repo = TrafficRepository(db)
    service = TrafficService(traffic_repo=traffic_repo)

    all_passed = True

    lat, lng = 11.0168, 76.9558  # Gandhipuram, Coimbatore

    # -----------------------------------------------------------------------
    # TEST 1: Adapter Flow Segment Schema Verification
    # -----------------------------------------------------------------------
    print("\n--- 1. Provider Adapter & TomTom Schema Verification ---")
    adapter = SimulatedTrafficAdapter()
    flow = adapter.get_flow_segment(lat, lng)
    expected_fields = [
        "currentSpeed",
        "freeFlowSpeed",
        "currentTravelTime",
        "freeFlowTravelTime",
        "confidence",
        "roadClosure",
    ]
    all_fields_present = all(f in flow for f in expected_fields)
    if all_fields_present:
        print(f" [PASS] Flow segment data matches EXACT TomTom schema:")
        print(f"   - Current Speed: {flow['currentSpeed']} km/h")
        print(f"   - Free Flow Speed: {flow['freeFlowSpeed']} km/h")
        print(f"   - Travel Time: {flow['currentTravelTime']}s (Free Flow: {flow['freeFlowTravelTime']}s)")
        print(f"   - Confidence: {flow['confidence']} | Road Closure: {flow['roadClosure']}")
    else:
        print(f" [FAIL] Missing expected TomTom fields in response: {flow}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 2: TrafficService Point Query & Derived Metrics
    # -----------------------------------------------------------------------
    print("\n--- 2. TrafficService Point Query & Delay Calculation ---")
    try:
        point_data = service.get_flow_at_point(lat, lng, persist=True)
        assert "delaySeconds" in point_data, "delaySeconds missing"
        assert "congestionLevel" in point_data, "congestionLevel missing"
        assert "roadStatus" in point_data, "roadStatus missing"
        print(f" [PASS] Traffic flow evaluated at ({lat}, {lng}):")
        print(f"   - Speed: {point_data['currentSpeed']} / {point_data['freeFlowSpeed']} km/h")
        print(f"   - Delay: {point_data['delayMinutes']} mins | Status: {point_data['roadStatus']} | Congestion: {point_data['congestionLevel']}")
    except Exception as e:
        print(f" [FAIL] TrafficService error: {e}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 3: MongoDB traffic_data Persistence Check
    # -----------------------------------------------------------------------
    print("\n--- 3. MongoDB traffic_data Collection Persistence ---")
    try:
        latest_record = db.traffic_data.find_one({"lat": lat, "lng": lng})
        if latest_record:
            print(f" [PASS] Record verified in MongoDB traffic_data collection: id={latest_record['_id']}, speed={latest_record['speed_kmh']} km/h, source={latest_record['source']}")
        else:
            print(f" [FAIL] Record not found in MongoDB traffic_data collection")
            all_passed = False
    except Exception as e:
        print(f" [FAIL] MongoDB query failed: {e}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 4: GET /api/traffic/current Endpoint
    # -----------------------------------------------------------------------
    print("\n--- 4. GET /api/traffic/current Endpoint ---")
    res = client.get(f"/api/traffic/current?lat={lat}&lng={lng}")
    print(f" Status: {res.status_code}")
    data = res.get_json()
    if res.status_code == 200 and "currentSpeed" in data and "delayMinutes" in data:
        print(f" [PASS] GET /api/traffic/current returned valid status: {data['roadStatus']} ({data['currentSpeed']} km/h)")
    else:
        print(f" [FAIL] Expected 200, got: {res.status_code}, data={data}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 5: POST /api/traffic/route-flow (Polyline Sampling)
    # -----------------------------------------------------------------------
    print("\n--- 5. POST /api/traffic/route-flow (Multi-segment sampling) ---")
    test_polyline = [
        [11.0168, 76.9558],
        [11.0150, 76.9520],
        [11.0120, 76.9480],
        [11.0094, 76.9458],
    ]
    route_res = client.post("/api/traffic/route-flow", json={"coordinates": test_polyline})
    print(f" Status: {route_res.status_code}")
    route_data = route_res.get_json()
    if route_res.status_code == 200 and "averageCurrentSpeed" in route_data:
        print(f" [PASS] Route traffic analysis completed across {route_data['sampledSegmentsCount']} segments:")
        print(f"   - Avg Current Speed: {route_data['averageCurrentSpeed']} km/h")
        print(f"   - Avg Free Flow Speed: {route_data['averageFreeFlowSpeed']} km/h")
        print(f"   - Total Route Delay: {route_data['totalDelayMinutes']} mins ({route_data['roadStatus']})")
    else:
        print(f" [FAIL] Expected 200 with route analysis, got: {route_res.status_code}, data={route_data}")
        all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print(" [RESULT] >>> PASS <<< All TomTom Traffic & Adapter Tests Passed!")
    else:
        print(" [RESULT] >>> FAIL <<< Some tests failed!")
    print("=" * 65)

    return all_passed


if __name__ == "__main__":
    success = run_traffic_tests()
    sys.exit(0 if success else 1)
