"""
backend/controllers/auth_controller.py — Authentication Controller.

Handles HTTP request validation, invokes AuthService, and formats clean JSON responses.
Never exposes raw passwords or internal server stack traces in responses.
"""
from __future__ import annotations

from flask import request, jsonify, g
from loguru import logger

from backend.services.auth_service import (
    AuthService,
    AuthError,
    DuplicateEmailError,
    InvalidCredentialsError,
    UserNotFoundError,
    ValidationError,
)

auth_service = AuthService()


def register_user():
    """Handle POST /api/auth/register"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "error": "bad_request",
            "message": "Request body must be a valid JSON object.",
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    try:
        result = auth_service.register(
            name=name,
            email=email,
            password=password,
            role=role,
        )
        return jsonify(result), 201

    except ValidationError as e:
        return jsonify({"error": "validation_error", "message": e.message}), e.status_code
    except DuplicateEmailError as e:
        return jsonify({"error": "conflict", "message": e.message}), e.status_code
    except AuthError as e:
        return jsonify({"error": "auth_error", "message": e.message}), e.status_code
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        return jsonify({"error": "internal_error", "message": "An unexpected error occurred during registration."}), 500


def login_user():
    """Handle POST /api/auth/login"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "error": "bad_request",
            "message": "Request body must be a valid JSON object.",
        }), 400

    email = data.get("email")
    password = data.get("password")

    try:
        result = auth_service.login(email=email, password=password)
        return jsonify(result), 200

    except ValidationError as e:
        return jsonify({"error": "validation_error", "message": e.message}), e.status_code
    except InvalidCredentialsError as e:
        return jsonify({"error": "unauthorized", "message": e.message}), e.status_code
    except AuthError as e:
        return jsonify({"error": "auth_error", "message": e.message}), e.status_code
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        return jsonify({"error": "internal_error", "message": "An unexpected error occurred during login."}), 500


def logout_user():
    """Handle POST /api/auth/logout"""
    try:
        result = auth_service.logout()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Unexpected error during logout: {e}")
        return jsonify({"error": "internal_error", "message": "An unexpected error occurred during logout."}), 500


def get_current_user():
    """Handle GET /api/auth/me (Protected)"""
    user_id = getattr(g, "current_user_id", None)
    if not user_id:
        return jsonify({"error": "unauthorized", "message": "User not authenticated."}), 401

    try:
        user = auth_service.get_current_user_profile(user_id)
        return jsonify({"user": user}), 200
    except UserNotFoundError as e:
        return jsonify({"error": "not_found", "message": e.message}), 404
    except Exception as e:
        logger.error(f"Unexpected error retrieving current user: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to retrieve user profile."}), 500


def admin_only_check():
    """Handle GET /api/auth/admin (Admin Only)"""
    user_id = getattr(g, "current_user_id", None)
    claims = getattr(g, "current_user_claims", {})
    return jsonify({
        "status": "success",
        "message": "Welcome to RouteIQ Admin Control Panel.",
        "admin_user_id": user_id,
        "role": claims.get("role"),
    }), 200
