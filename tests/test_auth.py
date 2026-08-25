"""
tests/test_auth.py — Complete JWT Authentication & Role-Based Access Tests.

Test Cases:
  1. Register success (201, returns access_token and user info)
  2. Register duplicate email (409 conflict)
  3. Login success (200, returns access_token)
  4. Login wrong password (401 unauthorized)
  5. Access protected route without token (401 unauthorized)
  6. Access protected route with user token (200 success)
  7. Access admin route as normal user (403 forbidden)
  8. Access admin route as admin user (200 success)
  9. Logout endpoint (200 success)
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Ensure project root is in sys.path
current = Path(__file__).resolve()
for p in [current.parent, current.parent.parent, current.parent.parent.parent]:
    if (p / "backend").exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

from backend.app import create_app
from backend.config.settings import TestingConfig
from backend.database import init_db, db


def run_auth_tests():
    print("=" * 65)
    print(" RouteIQ Phase 3: JWT Authentication & Roles Test Suite")
    print("=" * 65)

    test_config = TestingConfig()
    app = create_app(test_config)
    client = app.test_client()

    ts = int(datetime.now().timestamp())
    test_user_email = f"auth_user_{ts}@routeiq.com"
    test_admin_email = f"auth_admin_{ts}@routeiq.com"
    test_password = "SecurePassword123!"
    wrong_password = "WrongPassword999!"

    all_passed = True

    # -----------------------------------------------------------------------
    # TEST 1: Register Success
    # -----------------------------------------------------------------------
    print("\n--- 1. Register Success ---")
    reg_payload = {
        "name": "RouteIQ Regular User",
        "email": test_user_email,
        "password": test_password,
        "role": "user",
    }
    res = client.post("/api/auth/register", json=reg_payload)
    print(f" Status: {res.status_code}")
    data = res.get_json()
    if res.status_code == 201 and "access_token" in data and data["user"]["email"] == test_user_email:
        print(f" [PASS] User registered successfully with JWT access_token")
    else:
        print(f" [FAIL] Expected 201 with access_token, got: {res.status_code}, data={data}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 2: Register Duplicate Email (Expect 409)
    # -----------------------------------------------------------------------
    print("\n--- 2. Register Duplicate Email (Expect 409) ---")
    res = client.post("/api/auth/register", json=reg_payload)
    print(f" Status: {res.status_code}")
    data = res.get_json()
    if res.status_code == 409 and data.get("error") == "conflict":
        print(f" [PASS] Correctly rejected duplicate registration with 409 Conflict: {data.get('message')}")
    else:
        print(f" [FAIL] Expected 409 conflict, got: {res.status_code}, data={data}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 3: Login Success
    # -----------------------------------------------------------------------
    print("\n--- 3. Login Success ---")
    login_payload = {
        "email": test_user_email,
        "password": test_password,
    }
    res = client.post("/api/auth/login", json=login_payload)
    print(f" Status: {res.status_code}")
    data = res.get_json()
    user_token = data.get("access_token")
    if res.status_code == 200 and user_token and data["user"]["email"] == test_user_email:
        print(f" [PASS] Login successful, received JWT token for role='{data['user']['role']}'")
    else:
        print(f" [FAIL] Expected 200 with token, got: {res.status_code}, data={data}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 4: Login Wrong Password (Expect 401)
    # -----------------------------------------------------------------------
    print("\n--- 4. Login Wrong Password (Expect 401) ---")
    bad_login_payload = {
        "email": test_user_email,
        "password": wrong_password,
    }
    res = client.post("/api/auth/login", json=bad_login_payload)
    print(f" Status: {res.status_code}")
    data = res.get_json()
    if res.status_code == 401 and data.get("error") == "unauthorized":
        print(f" [PASS] Correctly rejected wrong password with 401 Unauthorized: {data.get('message')}")
    else:
        print(f" [FAIL] Expected 401, got: {res.status_code}, data={data}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 5: Access Protected Route Without Token (Expect 401)
    # -----------------------------------------------------------------------
    print("\n--- 5. Access Protected Route Without Token (Expect 401) ---")
    res = client.get("/api/auth/me")
    print(f" Status: {res.status_code}")
    data = res.get_json()
    if res.status_code == 401:
        print(f" [PASS] Unauthenticated request correctly blocked with 401: {data.get('message')}")
    else:
        print(f" [FAIL] Expected 401, got: {res.status_code}, data={data}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 6: Access Protected Route With User Token (Expect 200)
    # -----------------------------------------------------------------------
    print("\n--- 6. Access Protected Route With User Token (Expect 200) ---")
    headers = {"Authorization": f"Bearer {user_token}"}
    res = client.get("/api/auth/me", headers=headers)
    print(f" Status: {res.status_code}")
    data = res.get_json()
    if res.status_code == 200 and data.get("user", {}).get("email") == test_user_email:
        print(f" [PASS] Authenticated user profile retrieved: {data['user']['name']} ({data['user']['role']})")
        assert "password_hash" not in data["user"], "Security flaw: password_hash leaked!"
    else:
        print(f" [FAIL] Expected 200 with profile, got: {res.status_code}, data={data}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 7: Access Admin Route as Normal User (Expect 403)
    # -----------------------------------------------------------------------
    print("\n--- 7. Access Admin Route as Normal User (Expect 403) ---")
    res = client.get("/api/auth/admin", headers=headers)
    print(f" Status: {res.status_code}")
    data = res.get_json()
    if res.status_code == 403 and data.get("error") == "forbidden":
        print(f" [PASS] Regular user correctly denied access with 403 Forbidden: {data.get('message')}")
    else:
        print(f" [FAIL] Expected 403 Forbidden, got: {res.status_code}, data={data}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 8: Register Admin & Access Admin Route (Expect 200)
    # -----------------------------------------------------------------------
    print("\n--- 8. Register Admin & Access Admin Route (Expect 200) ---")
    admin_reg_payload = {
        "name": "RouteIQ Lead Admin",
        "email": test_admin_email,
        "password": test_password,
        "role": "admin",
    }
    res = client.post("/api/auth/register", json=admin_reg_payload)
    admin_token = res.get_json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    res_admin = client.get("/api/auth/admin", headers=admin_headers)
    print(f" Status: {res_admin.status_code}")
    admin_data = res_admin.get_json()
    if res_admin.status_code == 200 and admin_data.get("role") == "admin":
        print(f" [PASS] Admin successfully accessed admin route: {admin_data.get('message')}")
    else:
        print(f" [FAIL] Expected 200 for admin, got: {res_admin.status_code}, data={admin_data}")
        all_passed = False

    # -----------------------------------------------------------------------
    # TEST 9: Logout Endpoint (Expect 200)
    # -----------------------------------------------------------------------
    print("\n--- 9. Logout Endpoint (Expect 200) ---")
    res = client.post("/api/auth/logout")
    print(f" Status: {res.status_code}")
    data = res.get_json()
    if res.status_code == 200 and "Logged out" in data.get("message", ""):
        print(f" [PASS] Logout endpoint working cleanly: {data.get('message')}")
    else:
        print(f" [FAIL] Expected 200, got: {res.status_code}, data={data}")
        all_passed = False

    # -----------------------------------------------------------------------
    # Cleanup Test Users
    # -----------------------------------------------------------------------
    try:
        db.users.delete_many({"email": {"$in": [test_user_email, test_admin_email]}})
    except Exception:
        pass

    # -----------------------------------------------------------------------
    # Final Result
    # -----------------------------------------------------------------------
    print("\n" + "=" * 65)
    if all_passed:
        print(" [RESULT] >>> PASS <<< All Auth & Role-Based Access Tests Passed!")
    else:
        print(" [RESULT] >>> FAIL <<< Some Auth tests failed!")
    print("=" * 65)

    return all_passed


if __name__ == "__main__":
    success = run_auth_tests()
    sys.exit(0 if success else 1)
