"""
tests/conftest.py — Shared pytest fixtures for the RouteIQ test suite.

Provides:
  - Flask test client (in-memory MongoDB via mongomock)
  - Registered user & admin tokens for auth-dependent tests
  - Clean database state between tests
"""
import sys
import os
from pathlib import Path

# Ensure project root is on Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import mongomock
from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Flask App Fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def app():
    """Create a Flask test application with an isolated in-memory MongoDB."""
    os.environ["APP_ENV"] = "testing"
    os.environ["JWT_SECRET_KEY"] = "routeiq-test-secret-key-pytest"
    os.environ["MONGO_URI"] = "mongomock://localhost/routeiq_test"

    # Patch pymongo.MongoClient with mongomock before importing app
    with patch("pymongo.MongoClient", mongomock.MongoClient):
        from backend.app import create_app
        flask_app = create_app()
        flask_app.config["TESTING"] = True
        flask_app.config["JWT_SECRET_KEY"] = "routeiq-test-secret-key-pytest"
        yield flask_app


@pytest.fixture()
def client(app):
    """Flask test client, fresh per test."""
    with app.test_client() as c:
        yield c


@pytest.fixture()
def db(app):
    """Mongomock database handle for direct collection access."""
    with patch("pymongo.MongoClient", mongomock.MongoClient):
        client_mock = mongomock.MongoClient()
        yield client_mock["routeiq_test"]


# ---------------------------------------------------------------------------
# Auth Helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def user_token(client):
    """Register a standard user and return their JWT token."""
    payload = {
        "name": "Test User",
        "email": "pytest_user@routeiq.test",
        "password": "Test@12345!",
        "role": "user",
    }
    res = client.post("/api/auth/register", json=payload)
    if res.status_code == 409:
        # already exists — log in instead
        res = client.post("/api/auth/login", json={
            "email": payload["email"],
            "password": payload["password"],
        })
    data = res.get_json()
    token = data.get("access_token") or data.get("token")
    yield token
    # Cleanup: delete user after each test
    try:
        client.delete(f"/api/auth/users/pytest_user@routeiq.test")
    except Exception:
        pass


@pytest.fixture()
def admin_token(client):
    """Register an admin user and return their JWT token."""
    payload = {
        "name": "Test Admin",
        "email": "pytest_admin@routeiq.test",
        "password": "Admin@12345!",
        "role": "admin",
    }
    res = client.post("/api/auth/register", json=payload)
    if res.status_code == 409:
        res = client.post("/api/auth/login", json={
            "email": payload["email"],
            "password": payload["password"],
        })
    data = res.get_json()
    token = data.get("access_token") or data.get("token")
    yield token
