"""
tests/test_auth.py — pytest-based JWT Authentication & Role-Based Access Tests.

Tests:
  1. Register success (201, access_token returned)
  2. Register duplicate email (409 conflict)
  3. Login success (200, access_token returned)
  4. Login wrong password (401 unauthorized)
  5. Access protected route without token (401)
  6. Access protected route with valid user token (200)
  7. Access admin-only route as regular user (403)
  8. Access admin-only route as admin (200)
"""
import pytest
import uuid

# Each test uses a unique email to avoid cross-test collisions


def _unique_email(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}@routeiq.test"


# ---------------------------------------------------------------------------
# 1. Register Success
# ---------------------------------------------------------------------------

def test_register_success(client):
    email = _unique_email("reg")
    res = client.post("/api/auth/register", json={
        "name": "New User",
        "email": email,
        "password": "Test@12345!",
        "role": "user",
    })
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.get_json()}"
    data = res.get_json()
    assert "access_token" in data, "access_token missing from registration response"
    assert data["user"]["email"] == email
    assert "password_hash" not in data["user"], "password_hash must NOT be leaked"


# ---------------------------------------------------------------------------
# 2. Duplicate Email
# ---------------------------------------------------------------------------

def test_register_duplicate_email(client):
    email = _unique_email("dup")
    payload = {"name": "User A", "email": email, "password": "Test@12345!", "role": "user"}
    client.post("/api/auth/register", json=payload)  # first registration
    res = client.post("/api/auth/register", json=payload)  # duplicate
    assert res.status_code == 409, f"Expected 409 Conflict, got {res.status_code}"
    data = res.get_json()
    assert data.get("error") == "conflict"


# ---------------------------------------------------------------------------
# 3. Login Success
# ---------------------------------------------------------------------------

def test_login_success(client):
    email = _unique_email("login")
    pwd = "Login@12345!"
    client.post("/api/auth/register", json={
        "name": "Login User", "email": email, "password": pwd, "role": "user"
    })
    res = client.post("/api/auth/login", json={"email": email, "password": pwd})
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.get_json()}"
    data = res.get_json()
    assert "access_token" in data
    assert data["user"]["email"] == email


# ---------------------------------------------------------------------------
# 4. Wrong Password
# ---------------------------------------------------------------------------

def test_login_wrong_password(client):
    email = _unique_email("wrongpw")
    client.post("/api/auth/register", json={
        "name": "WP User", "email": email, "password": "Correct@99!", "role": "user"
    })
    res = client.post("/api/auth/login", json={"email": email, "password": "WrongPass@99!"})
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"
    data = res.get_json()
    assert data.get("error") == "unauthorized"


# ---------------------------------------------------------------------------
# 5. Unauthorized — no token
# ---------------------------------------------------------------------------

def test_access_protected_without_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401, f"Expected 401 without token, got {res.status_code}"


# ---------------------------------------------------------------------------
# 6. Authorized — valid user token
# ---------------------------------------------------------------------------

def test_access_protected_with_token(client):
    email = _unique_email("protected")
    pwd = "Protected@1!"
    reg = client.post("/api/auth/register", json={
        "name": "Protected User", "email": email, "password": pwd, "role": "user"
    })
    token = reg.get_json().get("access_token")
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.get_json()}"
    data = res.get_json()
    assert data["user"]["email"] == email
    assert "password_hash" not in data["user"], "password_hash must NOT be leaked"


# ---------------------------------------------------------------------------
# 7. Forbidden — regular user accessing admin route
# ---------------------------------------------------------------------------

def test_regular_user_forbidden_from_admin_route(client):
    email = _unique_email("forbidden")
    reg = client.post("/api/auth/register", json={
        "name": "Forbidden User", "email": email, "password": "Forbid@1!", "role": "user"
    })
    token = reg.get_json().get("access_token")
    res = client.get("/api/auth/admin", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403, f"Expected 403 Forbidden, got {res.status_code}"
    data = res.get_json()
    assert data.get("error") == "forbidden"


# ---------------------------------------------------------------------------
# 8. Admin can access admin route
# ---------------------------------------------------------------------------

def test_admin_can_access_admin_route(client):
    email = _unique_email("admin")
    reg = client.post("/api/auth/register", json={
        "name": "Admin User", "email": email, "password": "Admin@1!", "role": "admin"
    })
    token = reg.get_json().get("access_token")
    res = client.get("/api/auth/admin", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"Expected 200 for admin, got {res.status_code}: {res.get_json()}"
    data = res.get_json()
    assert data.get("role") == "admin"
