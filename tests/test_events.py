"""
tests/test_events.py — Events, Festivals, Marriages & Bottleneck Impact Test Suite.

Tests:
  1. Supported event types and schema validation
  2. POST /api/events (Create Festival & Marriage events)
  3. GET /api/events with filters and geographic radius
  4. Event impact formula calculation (crowd, proximity, time overlap)
  5. POST /api/events/route-impact (Multi-event polyline bottleneck evaluation)
  6. PUT /api/events/<event_id> (Update event)
  7. DELETE /api/events/<event_id> (Delete event)
"""
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Ensure project root is in sys.path
current = Path(__file__).resolve()
for p in [current.parent, current.parent.parent]:
    if (p / "backend").exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

from backend.app import create_app
from backend.config.settings import TestingConfig
from backend.services.event_service import EventService
from backend.repositories.event_repository import EventRepository
from backend.database import get_db


def run_event_tests():
    print("=" * 65)
    print(" RouteIQ Phase 9: Events, Festivals & Marriages Test Suite")
    print("=" * 65)

    app = create_app(TestingConfig())
    client = app.test_client()
    db = get_db()
    service = EventService(EventRepository(db))

    all_passed = True

    now = datetime.now(timezone.utc)
    future_start = now - timedelta(hours=1)
    future_end = now + timedelta(hours=5)

    # -----------------------------------------------------------------------
    # TEST 1: POST /api/events — Create Festival Event
    # -----------------------------------------------------------------------
    print("\n--- 1. Create Festival Event (POST /api/events) ---")
    festival_payload = {
        "title": "Koniamman Temple Car Festival (Grand Procession)",
        "event_type": "FESTIVAL",
        "description": "Annual temple car chariot procession attracting massive devotees along Town Hall corridor.",
        "venue_name": "Town Hall / Raja Street",
        "road_name": "Oppanakara Street & Raja St",
        "lat": 10.9950,
        "lng": 76.9600,
        "expected_crowd": 12000,
        "impact_level": "CRITICAL",
        "start_time": future_start.isoformat(),
        "end_time": future_end.isoformat(),
    }
    fest_res = client.post("/api/events", json=festival_payload)
    print(f" Status: {fest_res.status_code}")
    fest_data = fest_res.get_json()
    if fest_res.status_code == 201 and "event" in fest_data:
        fest_id = fest_data["event"]["_id"]
        print(f" [PASS] Festival created: id={fest_id}, type={fest_data['event']['event_type']}, impact={fest_data['event']['impact_level']}")
    else:
        print(f" [FAIL] Expected 201, got: {fest_res.status_code}, data={fest_data}")
        all_passed = False
        fest_id = None

    # -----------------------------------------------------------------------
    # TEST 2: POST /api/events — Create Marriage Event
    # -----------------------------------------------------------------------
    print("\n--- 2. Create Marriage Event (POST /api/events) ---")
    marriage_payload = {
        "title": "Grand Wedding Reception at Codissia Trade Fair Hall",
        "event_type": "MARRIAGE",
        "description": "High-profile wedding reception with 3,500 guests causing Avinashi Road feeder delays.",
        "venue_name": "Codissia Mandapam Hall D",
        "road_name": "Avinashi Road / Codissia Link",
        "lat": 11.0350,
        "lng": 77.0300,
        "expected_crowd": 3500,
        "impact_level": "HIGH",
        "start_time": future_start.isoformat(),
        "end_time": future_end.isoformat(),
    }
    marr_res = client.post("/api/events", json=marriage_payload)
    print(f" Status: {marr_res.status_code}")
    marr_data = marr_res.get_json()
    if marr_res.status_code == 201 and "event" in marr_data:
        marr_id = marr_data["event"]["_id"]
        print(f" [PASS] Marriage event created: id={marr_id}, type={marr_data['event']['event_type']}, crowd={marr_data['event']['expected_crowd']}")
    else:
        print(f" [FAIL] Expected 201, got: {marr_res.status_code}, data={marr_data}")
        all_passed = False
        marr_id = None

    # -----------------------------------------------------------------------
    # TEST 3: GET /api/events — List with Filters
    # -----------------------------------------------------------------------
    print("\n--- 3. List Events with Filters (GET /api/events) ---")
    # A. Filter by type=FESTIVAL
    list_fest = client.get("/api/events?type=FESTIVAL")
    print(f" Filter type=FESTIVAL Status: {list_fest.status_code}")
    data_f = list_fest.get_json()
    if list_fest.status_code == 200 and data_f.get("count", 0) >= 1:
        print(f" [PASS] Retrieved {data_f['count']} festival events")
    else:
        print(f" [FAIL] Expected >=1 festival, got {data_f}")
        all_passed = False

    # B. Filter by radius from Gandhipuram
    radius_res = client.get("/api/events?lat=11.0168&lng=76.9558&radius_km=15")
    print(f" Filter radius=15km Status: {radius_res.status_code}")
    data_r = radius_res.get_json()
    if radius_res.status_code == 200 and data_r.get("count", 0) >= 2:
        print(f" [PASS] Retrieved {data_r['count']} active events within 15km of Gandhipuram")
    else:
        print(f" [FAIL] Expected >=2 events in radius, got {data_r}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 4: Direct Event Impact Formula Verification
    # -----------------------------------------------------------------------
    print("\n--- 4. Event Impact Score Formula Verification ---")
    route_polyline = [
        [10.9945, 76.9595],  # Very close to Koniamman Temple (< 200m)
        [11.0000, 76.9610],
        [11.0100, 76.9550],
    ]
    if fest_data and "event" in fest_data:
        impact_calc = service.calculate_event_impact(fest_data["event"], route_polyline, now)
        print(f" Event Impact Score: {impact_calc['impact_score']} / 1.0 (Min Dist: {impact_calc['min_distance_m']}m)")
        print(f" Delay Multiplier: {impact_calc['delay_multiplier']}x | Impacting: {impact_calc['is_impacting']}")
        assert impact_calc["impact_score"] >= 0.70, f"Expected high impact >= 0.70, got {impact_calc['impact_score']}"
        print(" [PASS] Impact formula calculated accurate bottleneck score for close proximity festival")

    # -----------------------------------------------------------------------
    # TEST 5: POST /api/events/route-impact Endpoint
    # -----------------------------------------------------------------------
    print("\n--- 5. Route Polyline Impact Endpoint (POST /api/events/route-impact) ---")
    route_impact_res = client.post("/api/events/route-impact", json={"coordinates": route_polyline})
    print(f" Status: {route_impact_res.status_code}")
    r_impact_data = route_impact_res.get_json()
    if route_impact_res.status_code == 200 and "total_impact_score" in r_impact_data:
        print(f" [PASS] Route evaluated: total_impact_score={r_impact_data['total_impact_score']}, impacting_events={r_impact_data['impacting_events_count']}")
    else:
        print(f" [FAIL] Expected 200, got: {route_impact_res.status_code}, data={r_impact_data}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 6: PUT /api/events/<id> — Update Event
    # -----------------------------------------------------------------------
    print("\n--- 6. Update Event (PUT /api/events/<id>) ---")
    if fest_id:
        upd_res = client.put(f"/api/events/{fest_id}", json={"expected_crowd": 15000, "venue_name": "Town Hall Main Junction"})
        print(f" Status: {upd_res.status_code}")
        upd_data = upd_res.get_json()
        if upd_res.status_code == 200 and upd_data.get("event", {}).get("expected_crowd") == 15000:
            print(f" [PASS] Event updated: crowd={upd_data['event']['expected_crowd']}")
        else:
            print(f" [FAIL] Expected 200, got: {upd_res.status_code}, data={upd_data}")
            all_passed = False

    # -----------------------------------------------------------------------
    # TEST 7: DELETE /api/events/<id> — Delete Event
    # -----------------------------------------------------------------------
    print("\n--- 7. Delete Event (DELETE /api/events/<id>) ---")
    if marr_id:
        del_res = client.delete(f"/api/events/{marr_id}")
        print(f" Status: {del_res.status_code}")
        if del_res.status_code == 200:
            print(f" [PASS] Event {marr_id} deleted cleanly.")
        else:
            print(f" [FAIL] Expected 200, got: {del_res.status_code}")
            all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print(" [RESULT] >>> PASS <<< All Events & Bottleneck Tests Passed!")
    else:
        print(" [RESULT] >>> FAIL <<< Some event tests failed!")
    print("=" * 65)

    return all_passed


if __name__ == "__main__":
    success = run_event_tests()
    sys.exit(0 if success else 1)
