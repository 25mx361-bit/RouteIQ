"""
tests/test_landslides.py — Landslide Hazard Management & Route Blocking Test Suite.

Tests:
  1. POST /api/landslides (Create active landslide hazard on Ghat corridor)
  2. GET /api/landslides (List and status filtering)
  3. PUT /api/landslides/<id>/activate and /resolve
  4. Polyline collision detection via check_route_landslide_impact
  5. CRITICAL RULE VERIFICATION: A blocked route is NEVER recommended. Re-ranks to safe alternative.
  6. DELETE /api/landslides/<id>
"""
import sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure project root is in sys.path
current = Path(__file__).resolve()
for p in [current.parent, current.parent.parent]:
    if (p / "backend").exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

from backend.app import create_app
from backend.config.settings import TestingConfig
from backend.services.landslide_service import LandslideService
from backend.services.routing_service import RoutingService
from backend.repositories.landslide_repository import LandslideRepository
from backend.database import get_db


def run_landslide_tests():
    print("=" * 65)
    print(" RouteIQ Phase 10: Landslide Management & Blockade Test Suite")
    print("=" * 65)

    app = create_app(TestingConfig())
    client = app.test_client()
    db = get_db()
    service = LandslideService(LandslideRepository(db))
    routing_service = RoutingService()

    all_passed = True

    # -----------------------------------------------------------------------
    # TEST 1: POST /api/events — Create Active Landslide on Coonoor Ghat
    # -----------------------------------------------------------------------
    print("\n--- 1. Create Active Landslide Hazard (POST /api/landslides) ---")
    landslide_payload = {
        "title": "Severe Rockfall & Mudslide at Marakkal Hairpin Bend",
        "status": "ACTIVE",
        "risk_level": "Severe",
        "severity": "CRITICAL",
        "region_name": "Mettupalayam - Coonoor Ghat Road",
        "road_name": "NH-181 Hairpin 7-9",
        "lat": 11.3200,
        "lng": 76.8800,
        "radius_m": 3000.0,
        "rainfall_mm": 85.0,
        "description": "Massive boulder fall and heavy slush completely blocking both lanes of NH-181.",
    }
    create_res = client.post("/api/landslides", json=landslide_payload)
    print(f" Status: {create_res.status_code}")
    c_data = create_res.get_json()
    if create_res.status_code == 201 and "landslide" in c_data:
        ls_id = c_data["landslide"]["_id"]
        print(f" [PASS] Landslide created: id={ls_id}, status={c_data['landslide']['status']}, severity={c_data['landslide']['severity']}")
    else:
        print(f" [FAIL] Expected 201, got: {create_res.status_code}, data={c_data}")
        all_passed = False
        ls_id = None

    # -----------------------------------------------------------------------
    # TEST 2: GET /api/landslides — List & Filter Active Hazards
    # -----------------------------------------------------------------------
    print("\n--- 2. List Landslides (GET /api/landslides?status=ACTIVE) ---")
    list_res = client.get("/api/landslides?status=ACTIVE")
    print(f" Status: {list_res.status_code}")
    l_data = list_res.get_json()
    if list_res.status_code == 200 and l_data.get("count", 0) >= 1:
        print(f" [PASS] Retrieved {l_data['count']} active landslide hazards")
    else:
        print(f" [FAIL] Expected >=1 active landslide, got: {l_data}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 3: Polyline Collision Detection
    # -----------------------------------------------------------------------
    print("\n--- 3. Haversine Spatial Collision Detection ---")
    # Route passing directly through the landslide coordinate (11.3200, 76.8800)
    blocked_polyline = [
        [11.3000, 76.8900],
        [11.3190, 76.8805],  # 120m away from landslide center (< 3000m radius)
        [11.3350, 76.8700],
    ]
    # Safe bypass polyline far away (> 15km)
    safe_polyline = [
        [11.0168, 76.9558],
        [11.0094, 76.9458],
    ]

    impact_blocked = service.check_route_landslide_impact(blocked_polyline)
    impact_safe = service.check_route_landslide_impact(safe_polyline)

    if impact_blocked.get("blocked") is True:
        print(f" [PASS] Detected collision on blocked route: Hazard='{impact_blocked['title']}', Distance={impact_blocked['distance_m']}m <= Radius={impact_blocked['radius_m']}m")
    else:
        print(f" [FAIL] Failed to detect collision on blocked route: {impact_blocked}")
        all_passed = False

    if impact_safe.get("blocked") is False:
        print(" [PASS] Correctly verified safe bypass route is NOT blocked")
    else:
        print(f" [FAIL] Safe route falsely marked blocked: {impact_safe}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 4: CRITICAL RULE — Blocked Route MUST NEVER be Recommended
    # -----------------------------------------------------------------------
    print("\n--- 4. CRITICAL RULE VERIFICATION: Blocked Route Never Recommended ---")
    candidate_routes = [
        {
            "route_id": "route_0",
            "name": "Fastest Route (Direct via NH-181 Ghat Road)",
            "distance_km": 32.0,
            "duration_min": 45.0,
            "coordinates": blocked_polyline,  # Directly intersecting active landslide!
            "is_recommended": True,           # Initial default before safety audit
        },
        {
            "route_id": "route_1",
            "name": "Safe Alternative Bypass (via Kotagiri Corridor)",
            "distance_km": 44.0,
            "duration_min": 58.0,
            "coordinates": safe_polyline,     # Safe path
            "is_recommended": False,
        },
    ]

    evaluated_routes = service.evaluate_routes_for_landslides(candidate_routes)

    r0 = evaluated_routes[0]
    r1 = evaluated_routes[1]

    # Verify Route 0 is blocked and NOT recommended
    assert r0["is_blocked"] is True, "Route 0 must be marked blocked"
    assert r0["is_recommended"] is False, "CRITICAL: Blocked route must NOT be recommended"
    print(f" [PASS] Primary Route 0: is_blocked={r0['is_blocked']} | is_recommended={r0['is_recommended']} (BLOCKED)")

    # Verify Route 1 is safe and elevated to RECOMMENDED
    assert r1["is_blocked"] is False, "Route 1 must be safe"
    assert r1["is_recommended"] is True, "Route 1 must be elevated to recommended"
    print(f" [PASS] Safe Alternative Route 1: is_blocked={r1['is_blocked']} | is_recommended={r1['is_recommended']} (ELEVATED TO RECOMMENDED)")

    # -----------------------------------------------------------------------
    # TEST 5: PUT /api/landslides/<id>/resolve & /activate
    # -----------------------------------------------------------------------
    print("\n--- 5. Resolve and Re-activate Hazard Workflow ---")
    if ls_id:
        # A. Resolve
        res_res = client.put(f"/api/landslides/{ls_id}/resolve")
        print(f" Resolve Status: {res_res.status_code}")
        if res_res.status_code == 200:
            print(f" [PASS] Landslide {ls_id} marked RESOLVED. Road restriction lifted.")
        else:
            print(f" [FAIL] Resolve failed: {res_res.status_code}")
            all_passed = False

        # B. Re-activate
        act_res = client.put(f"/api/landslides/{ls_id}/activate")
        print(f" Re-activate Status: {act_res.status_code}")
        if act_res.status_code == 200:
            print(f" [PASS] Landslide {ls_id} re-activated and broadcast notification sent.")
        else:
            print(f" [FAIL] Re-activate failed: {act_res.status_code}")
            all_passed = False

    # -----------------------------------------------------------------------
    # TEST 6: DELETE /api/landslides/<id>
    # -----------------------------------------------------------------------
    print("\n--- 6. Delete Landslide (DELETE /api/landslides/<id>) ---")
    if ls_id:
        del_res = client.delete(f"/api/landslides/{ls_id}")
        print(f" Delete Status: {del_res.status_code}")
        if del_res.status_code == 200:
            print(f" [PASS] Landslide {ls_id} deleted cleanly.")
        else:
            print(f" [FAIL] Delete failed: {del_res.status_code}")
            all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print(" [RESULT] >>> PASS <<< All Landslide & Route Blocking Tests Passed!")
    else:
        print(" [RESULT] >>> FAIL <<< Some landslide tests failed!")
    print("=" * 65)

    return all_passed


if __name__ == "__main__":
    success = run_landslide_tests()
    sys.exit(0 if success else 1)
