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
    admin_only_check,
    forgot_password_request,
    reset_password_submit,
    update_profile,
    change_password,
)
from backend.controllers.user_controller import get_current_user_profile
from backend.middleware.auth_middleware import require_auth, require_admin

auth_routes_bp = Blueprint("auth_routes", __name__)

# Public Auth Routes
auth_routes_bp.post("/register")(register_user)
auth_routes_bp.post("/login")(login_user)
auth_routes_bp.post("/logout")(logout_user)
auth_routes_bp.post("/forgot-password")(forgot_password_request)
auth_routes_bp.post("/reset-password")(reset_password_submit)

# Protected User Routes
auth_routes_bp.get("/me")(require_auth(get_current_user_profile))
auth_routes_bp.put("/profile")(require_auth(update_profile))
auth_routes_bp.post("/change-password")(require_auth(change_password))

# Protected Admin Route
auth_routes_bp.get("/admin")(require_admin(admin_only_check))
