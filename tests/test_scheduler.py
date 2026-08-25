"""
tests/test_scheduler.py — APScheduler Background Engine & Admin Endpoint Tests.

Tests:
  1. Scheduler initialization and registration of all 4 data collection jobs
  2. Manual execution of traffic_data_collection job
  3. Manual execution of weather_data_collection job
  4. Manual execution of event_status_update job
  5. Manual execution of notification_check job
  6. Persistence of scheduler logs in MongoDB system_logs collection
  7. GET /api/admin/scheduler/status endpoint verification
  8. POST /api/admin/scheduler/trigger-job endpoint verification
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
from backend.scheduler.scheduler import init_scheduler, get_scheduler_status, shutdown_scheduler
from backend.scheduler.jobs import (
    traffic_data_collection,
    weather_data_collection,
    event_status_update,
    notification_check,
)
from backend.database import get_db


def run_scheduler_tests():
    print("=" * 65)
    print(" RouteIQ Phase 8: APScheduler Data Collection Test Suite")
    print("=" * 65)

    app = create_app(TestingConfig())
    client = app.test_client()
    db = get_db()

    all_passed = True

    # -----------------------------------------------------------------------
    # TEST 1: APScheduler Job Registration
    # -----------------------------------------------------------------------
    print("\n--- 1. APScheduler Initialization & Job Registration ---")
    sched = init_scheduler(app)
    jobs = sched.get_jobs()
    job_ids = [j.id for j in jobs]
    expected_jobs = [
        "traffic_data_collection",
        "weather_data_collection",
        "event_status_update",
        "notification_check",
    ]
    registered_all = all(j in job_ids for j in expected_jobs)
    if registered_all:
        print(f" [PASS] All {len(jobs)} expected background collection jobs registered:")
        for j in jobs:
            print(f"   - Job ID: '{j.id}' | Trigger: {j.trigger}")
    else:
        print(f" [FAIL] Missing expected jobs. Registered: {job_ids}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 2: traffic_data_collection Execution
    # -----------------------------------------------------------------------
    print("\n--- 2. Job Execution: traffic_data_collection ---")
    try:
        t_res = traffic_data_collection()
        assert t_res.get("status") in ("SUCCESS", "PARTIAL"), f"Unexpected status: {t_res}"
        print(f" [PASS] traffic_data_collection finished: status={t_res.get('status')}, records={t_res.get('records_collected')}")
    except Exception as e:
        print(f" [FAIL] traffic_data_collection failed: {e}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 3: weather_data_collection Execution
    # -----------------------------------------------------------------------
    print("\n--- 3. Job Execution: weather_data_collection ---")
    try:
        w_res = weather_data_collection()
        assert w_res.get("status") in ("SUCCESS", "PARTIAL"), f"Unexpected status: {w_res}"
        print(f" [PASS] weather_data_collection finished: status={w_res.get('status')}, records={w_res.get('records_collected')}")
    except Exception as e:
        print(f" [FAIL] weather_data_collection failed: {e}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 4: event_status_update Execution
    # -----------------------------------------------------------------------
    print("\n--- 4. Job Execution: event_status_update ---")
    try:
        e_res = event_status_update()
        assert e_res.get("status") == "SUCCESS", f"Unexpected status: {e_res}"
        print(f" [PASS] event_status_update finished: status={e_res.get('status')}, records_updated={e_res.get('records_updated')}")
    except Exception as e:
        print(f" [FAIL] event_status_update failed: {e}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 5: notification_check Execution
    # -----------------------------------------------------------------------
    print("\n--- 5. Job Execution: notification_check ---")
    try:
        n_res = notification_check()
        assert n_res.get("status") == "SUCCESS", f"Unexpected status: {n_res}"
        print(f" [PASS] notification_check finished: status={n_res.get('status')}, alerts_dispatched={n_res.get('alerts_dispatched')}")
    except Exception as e:
        print(f" [FAIL] notification_check failed: {e}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 6: MongoDB system_logs Verification
    # -----------------------------------------------------------------------
    print("\n--- 6. MongoDB system_logs Persistence Verification ---")
    try:
        log_entry = db.system_logs.find_one({"source": "scheduler.traffic_data_collection"})
        if log_entry:
            print(f" [PASS] Found scheduler audit record in MongoDB system_logs: id={log_entry['_id']}, msg='{log_entry.get('message')}'")
        else:
            print(f" [FAIL] No scheduler audit records found in system_logs")
            all_passed = False
    except Exception as e:
        print(f" [FAIL] system_logs lookup failed: {e}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 7: GET /api/admin/scheduler/status Endpoint
    # -----------------------------------------------------------------------
    print("\n--- 7. GET /api/admin/scheduler/status Endpoint ---")
    res = client.get("/api/admin/scheduler/status")
    print(f" Status: {res.status_code}")
    data = res.get_json()
    if res.status_code == 200 and "jobs" in data and len(data["jobs"]) >= 4:
        print(f" [PASS] Admin scheduler status returned {len(data['jobs'])} jobs (Status: {data['scheduler_status']}):")
        for j in data["jobs"]:
            print(f"   - {j['name']}: Interval={j['interval']} | Last Status={j['last_status']} | Duration={j['last_duration_ms']}ms")
    else:
        print(f" [FAIL] Expected 200 with >=4 jobs, got: {res.status_code}, data={data}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 8: POST /api/admin/scheduler/trigger-job Endpoint
    # -----------------------------------------------------------------------
    print("\n--- 8. POST /api/admin/scheduler/trigger-job Endpoint ---")
    trig_res = client.post("/api/admin/scheduler/trigger-job", json={"job_id": "weather_data_collection"})
    print(f" Status: {trig_res.status_code}")
    trig_data = trig_res.get_json()
    if trig_res.status_code == 200 and trig_data.get("job_id") == "weather_data_collection":
        print(f" [PASS] Admin manual job trigger successful: {trig_data.get('message')}")
    else:
        print(f" [FAIL] Expected 200, got: {trig_res.status_code}, data={trig_data}")
        all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print(" [RESULT] >>> PASS <<< All APScheduler & Admin Tests Passed!")
    else:
        print(" [RESULT] >>> FAIL <<< Some scheduler tests failed!")
    print("=" * 65)

    return all_passed


if __name__ == "__main__":
    success = run_scheduler_tests()
    sys.exit(0 if success else 1)
