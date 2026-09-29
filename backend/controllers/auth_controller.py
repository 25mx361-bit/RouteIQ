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
    phone = data.get("phone", "")

    try:
        result = auth_service.register(
            name=name,
            email=email,
            password=password,
            role=role,
            phone=phone,
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


def forgot_password_request():
    """Handle POST /api/auth/forgot-password"""
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    try:
        result = auth_service.request_password_reset(email=email)
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"error": "validation_error", "message": e.message}), e.status_code
    except UserNotFoundError as e:
        return jsonify({"error": "not_found", "message": e.message}), 404
    except Exception as e:
        logger.error(f"Unexpected error in forgot_password: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to process reset request."}), 500


def reset_password_submit():
    """Handle POST /api/auth/reset-password"""
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    token = data.get("token") or data.get("reset_token")
    new_password = data.get("new_password") or data.get("password")

    try:
        result = auth_service.reset_password(
            email=email,
            token=token,
            new_password=new_password,
        )
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"error": "validation_error", "message": e.message}), e.status_code
    except UserNotFoundError as e:
        return jsonify({"error": "not_found", "message": e.message}), 404
    except Exception as e:
        logger.error(f"Unexpected error in reset_password: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to reset password."}), 500


def update_profile():
    """Handle PUT /api/auth/profile (Protected)"""
    user_id = getattr(g, "current_user_id", None)
    if not user_id:
        return jsonify({"error": "unauthorized", "message": "User not authenticated."}), 401

    data = request.get_json(silent=True) or {}
    name = data.get("name") or data.get("fullName") or ""
    phone = data.get("phone") or ""

    try:
        result = auth_service.update_profile(user_id=user_id, name=name, phone=phone)
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"error": "validation_error", "message": e.message}), e.status_code
    except UserNotFoundError as e:
        return jsonify({"error": "not_found", "message": e.message}), 404
    except Exception as e:
        logger.error(f"Unexpected error in update_profile: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to update profile."}), 500


def change_password():
    """Handle POST /api/auth/change-password (Protected)"""
    user_id = getattr(g, "current_user_id", None)
    if not user_id:
        return jsonify({"error": "unauthorized", "message": "User not authenticated."}), 401

    data = request.get_json(silent=True) or {}
    old_password = data.get("old_password") or data.get("current_password") or ""
    new_password = data.get("new_password") or ""

    try:
        result = auth_service.change_password(
            user_id=user_id,
            old_password=old_password,
            new_password=new_password,
        )
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"error": "validation_error", "message": e.message}), e.status_code
    except InvalidCredentialsError as e:
        return jsonify({"error": "unauthorized", "message": e.message}), e.status_code
    except UserNotFoundError as e:
        return jsonify({"error": "not_found", "message": e.message}), 404
    except Exception as e:
        logger.error(f"Unexpected error in change_password: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to change password."}), 500

