"""
backend/routes/auth_routes.py — Authentication & RBAC Routes.

Endpoints:
  POST /api/auth/register  — Register new user (USER or ADMIN)
  POST /api/auth/login     — Login with email & password, returns JWT token
  POST /api/auth/logout    — Logout user
  GET  /api/auth/me        — Get current user profile (Requires Auth)
  GET  /api/auth/admin     — Admin-only protected test endpoint (Requires Admin)
"""
from __future__ import annotations

from flask import Blueprint
from backend.controllers.auth_controller import (
    register_user,
    login_user,
    logout_user,
    get_current_user,
    admin_only_check,
)
from backend.middleware.auth_middleware import require_auth, require_admin

auth_routes_bp = Blueprint("auth_routes", __name__)

# Public Auth Routes
auth_routes_bp.post("/register")(register_user)
auth_routes_bp.post("/login")(login_user)
auth_routes_bp.post("/logout")(logout_user)

# Protected User Route
auth_routes_bp.get("/me")(require_auth(get_current_user))

# Protected Admin Route
auth_routes_bp.get("/admin")(require_admin(admin_only_check))
