"""
tests/test_db.py — Comprehensive CRUD Verification for RouteIQ MongoDB Models & Repositories.

Tests:
  1. User Model & Repository CRUD:
     - Insert a test user document
     - Read it back
     - Update it
     - Delete it
  2. Multi-collection schema validation across:
     - traffic_data, weather_data, routes, predictions, events,
       landslides, notifications, search_history, model_logs, system_logs
  3. Prints PASS / FAIL status clearly.
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# Ensure project root is in sys.path regardless of where test is invoked
current = Path(__file__).resolve()
for p in [current.parent, current.parent.parent, current.parent.parent.parent]:
    if (p / "backend").exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

from pymongo.errors import ConnectionFailure
from backend.models import (
    UserModel,
    TrafficDataModel,
    WeatherDataModel,
    RouteModel,
    PredictionModel,
    EventModel,
    LandslideModel,
    NotificationModel,
    SearchHistoryModel,
    ModelLogModel,
    SystemLogModel,
)
from backend.repositories import (
    UserRepository,
    TrafficRepository,
    WeatherRepository,
    RouteRepository,
    PredictionRepository,
    EventRepository,
    LandslideRepository,
    NotificationRepository,
    SearchHistoryRepository,
    ModelLogRepository,
    SystemLogRepository,
)
from backend.database import init_db, close_db


def get_test_db():
    """Connect to real MongoDB if available, otherwise use mongomock Database."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/routeiq_test")
    try:
        db = init_db(mongo_uri)
        # Test basic connection ping
        db.command("ping")
        print(f"[INFO] Connected to live MongoDB: {mongo_uri}")
        return db, False
    except Exception as e:
        print(f"[INFO] Live MongoDB unavailable ({e}), using mongomock test database...")
        import mongomock
        mock_client = mongomock.MongoClient()
        mock_db = mock_client["routeiq_test"]
        return mock_db, True


def run_crud_tests():
    print("=" * 65)
    print(" RouteIQ MongoDB Schema & CRUD Verification")
    print("=" * 65)

    test_db, is_mock = get_test_db()
    all_passed = True

    # -----------------------------------------------------------------------
    # TEST 1: User CRUD (Insert -> Read -> Update -> Delete)
    # -----------------------------------------------------------------------
    print("\n--- 1. User Model & Repository CRUD ---")
    user_repo = UserRepository(test_db)
    test_email = f"test_user_{int(datetime.now().timestamp())}@example.com"
    test_user_data = {
        "name": "RouteIQ Test User",
        "email": test_email,
        "password_hash": "$2b$12$e8YkZ8h38uX84Y.1yL3/2e3X.aB4s5W3.gT9HjKl10.zQWErtYui",
        "role": "user",
    }

    try:
        # A. Insert
        user_id = user_repo.create(test_user_data)
        assert user_id is not None and len(user_id) > 0, "Insert failed: No user ID returned"
        print(f" [PASS] Insert User: inserted_id = {user_id}")

        # B. Read
        user = user_repo.get_by_id(user_id)
        assert user is not None, "Read failed: User not found by ID"
        assert user["email"] == test_email.lower(), f"Read mismatch: {user['email']} != {test_email.lower()}"
        assert user["name"] == "RouteIQ Test User", "Name mismatch"
        assert "created_at" in user, "created_at timestamp missing"
        print(f" [PASS] Read User by ID: found {user['name']} ({user['email']})")

        # C. Read by Email
        user_by_email = user_repo.get_by_email(test_email)
        assert user_by_email is not None, "Read by email failed"
        print(f" [PASS] Read User by Email: {test_email}")

        # D. Update
        update_ok = user_repo.update(user_id, {"name": "RouteIQ Updated User", "role": "admin"})
        assert update_ok, "Update failed: matched_count == 0"
        updated_user = user_repo.get_by_id(user_id)
        assert updated_user["name"] == "RouteIQ Updated User", "Updated name mismatch"
        assert updated_user["role"] == "admin", "Updated role mismatch"
        print(f" [PASS] Update User: new name = '{updated_user['name']}', role = '{updated_user['role']}'")

        # E. Delete
        delete_ok = user_repo.delete(user_id)
        assert delete_ok, "Delete failed"
        deleted_user = user_repo.get_by_id(user_id)
        assert deleted_user is None, "User still exists after delete"
        print(f" [PASS] Delete User: successfully removed ID = {user_id}")

    except Exception as e:
        print(f" [FAIL] User CRUD Error: {e}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 2: All Other Models & Repositories CRUD Verification
    # -----------------------------------------------------------------------
    print("\n--- 2. All Collections Schema & CRUD Verification ---")

    now = datetime.now(timezone.utc)

    # 2. Traffic Data
    try:
        traffic_repo = TrafficRepository(test_db)
        t_id = traffic_repo.create({
            "segment_id": "seg_101",
            "road_id": "Anna Salai - NH45",
            "timestamp": now,
            "speed_kmh": 32.5,
            "free_flow_speed": 50.0,
            "source": "tomtom",
        })
        t_doc = traffic_repo.get_by_id(t_id)
        assert t_doc and t_doc["segment_id"] == "seg_101"
        traffic_repo.delete(t_id)
        print(" [PASS] traffic_data CRUD")
    except Exception as e:
        print(f" [FAIL] traffic_data CRUD: {e}")
        all_passed = False

    # 3. Weather Data
    try:
        weather_repo = WeatherRepository(test_db)
        w_id = weather_repo.create({
            "timestamp": now,
            "lat": 13.0827,
            "lng": 80.2707,
            "temperature": 31.2,
            "source": "open_meteo",
        })
        w_doc = weather_repo.get_by_id(w_id)
        assert w_doc and w_doc["temperature"] == 31.2
        weather_repo.delete(w_id)
        print(" [PASS] weather_data CRUD")
    except Exception as e:
        print(f" [FAIL] weather_data CRUD: {e}")
        all_passed = False

    # 4. Routes
    try:
        route_repo = RouteRepository(test_db)
        r_id = route_repo.create({
            "source": {"lat": 13.0827, "lng": 80.2707, "label": "Chennai Central"},
            "destination": {"lat": 12.9815, "lng": 80.2180, "label": "Guindy"},
            "distance_m": 12400.0,
            "duration_s": 1820.0,
        })
        r_doc = route_repo.get_by_id(r_id)
        assert r_doc and r_doc["distance_m"] == 12400.0
        route_repo.delete(r_id)
        print(" [PASS] routes CRUD")
    except Exception as e:
        print(f" [FAIL] routes CRUD: {e}")
        all_passed = False

    # 5. Predictions
    try:
        pred_repo = PredictionRepository(test_db)
        p_id = pred_repo.create({
            "user_id": "test_user_id",
            "source": {"lat": 13.0827, "lng": 80.2707, "label": "Start"},
            "destination": {"lat": 12.9815, "lng": 80.2180, "label": "End"},
            "travel_datetime": now,
            "congestion_level": "Medium",
            "recommendation": {"route_index": 0, "score": 0.88},
        })
        p_doc = pred_repo.get_by_id(p_id)
        assert p_doc and p_doc["congestion_level"] == "Medium"
        pred_repo.delete(p_id)
        print(" [PASS] predictions CRUD")
    except Exception as e:
        print(f" [FAIL] predictions CRUD: {e}")
        all_passed = False

    # 6. Events
    try:
        event_repo = EventRepository(test_db)
        e_id = event_repo.create({
            "title": "Road Maintenance",
            "event_type": "construction",
            "severity": "medium",
            "location": {"type": "Point", "coordinates": [80.2707, 13.0827]},
            "timestamp": now,
        })
        e_doc = event_repo.get_by_id(e_id)
        assert e_doc and e_doc["title"] == "Road Maintenance"
        event_repo.delete(e_id)
        print(" [PASS] events CRUD")
    except Exception as e:
        print(f" [FAIL] events CRUD: {e}")
        all_passed = False

    # 7. Landslides
    try:
        landslide_repo = LandslideRepository(test_db)
        l_id = landslide_repo.create({
            "title": "Ghat Road Warning",
            "risk_level": "High",
            "location": {"type": "Point", "coordinates": [76.9558, 11.0168]},
            "reported_at": now,
        })
        l_doc = landslide_repo.get_by_id(l_id)
        assert l_doc and l_doc["risk_level"] == "High"
        landslide_repo.delete(l_id)
        print(" [PASS] landslides CRUD")
    except Exception as e:
        print(f" [FAIL] landslides CRUD: {e}")
        all_passed = False

    # 8. Notifications
    try:
        notif_repo = NotificationRepository(test_db)
        n_id = notif_repo.create({
            "user_id": "test_user_id",
            "title": "Congestion Alert",
            "message": "High congestion expected on your usual route.",
        })
        n_doc = notif_repo.get_by_id(n_id)
        assert n_doc and n_doc["is_read"] is False
        notif_repo.mark_as_read(n_id)
        n_updated = notif_repo.get_by_id(n_id)
        assert n_updated["is_read"] is True
        notif_repo.delete(n_id)
        print(" [PASS] notifications CRUD")
    except Exception as e:
        print(f" [FAIL] notifications CRUD: {e}")
        all_passed = False

    # 9. Search History
    try:
        search_repo = SearchHistoryRepository(test_db)
        s_id = search_repo.create({
            "user_id": "test_user_id",
            "source_query": "Chennai",
            "destination_query": "Coimbatore",
        })
        s_doc = search_repo.get_by_id(s_id)
        assert s_doc and s_doc["source_query"] == "Chennai"
        search_repo.delete(s_id)
        print(" [PASS] search_history CRUD")
    except Exception as e:
        print(f" [FAIL] search_history CRUD: {e}")
        all_passed = False

    # 10. Model Logs
    try:
        mlog_repo = ModelLogRepository(test_db)
        m_id = mlog_repo.create({
            "model_name": "PatchTST",
            "run_type": "inference",
            "status": "SUCCESS",
        })
        m_doc = mlog_repo.get_by_id(m_id)
        assert m_doc and m_doc["model_name"] == "PatchTST"
        mlog_repo.delete(m_id)
        print(" [PASS] model_logs CRUD")
    except Exception as e:
        print(f" [FAIL] model_logs CRUD: {e}")
        all_passed = False

    # 11. System Logs
    try:
        syslog_repo = SystemLogRepository(test_db)
        log_id = syslog_repo.log(
            level="INFO",
            source="test.crud",
            message="CRUD test execution log",
            details={"phase": 2},
        )
        log_doc = syslog_repo.get_by_id(log_id)
        assert log_doc and log_doc["level"] == "INFO"
        syslog_repo.delete(log_id)
        print(" [PASS] system_logs CRUD")
    except Exception as e:
        print(f" [FAIL] system_logs CRUD: {e}")
        all_passed = False

    # -----------------------------------------------------------------------
    # Final Result
    # -----------------------------------------------------------------------
    print("\n" + "=" * 65)
    if all_passed:
        print(" [RESULT] >>> PASS <<< All 11 Models & Repositories CRUD Verified!")
    else:
        print(" [RESULT] >>> FAIL <<< Some CRUD tests failed!")
    print("=" * 65)

    return all_passed


if __name__ == "__main__":
    success = run_crud_tests()
    sys.exit(0 if success else 1)
