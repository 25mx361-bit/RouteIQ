"""
backend/middleware/auth_middleware.py — JWT & Role-based Access Control Decorators.

Provides:
  - @require_auth: Ensures valid JWT token is present in Authorization header
  - @require_admin: Ensures valid JWT token is present AND user has 'admin' role
"""
from __future__ import annotations

from functools import wraps
from typing import Callable
from flask import jsonify, g, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from flask_jwt_extended.exceptions import JWTExtendedException
from loguru import logger


def require_auth(fn: Callable) -> Callable:
    """
    Decorator to protect routes requiring a valid JWT token.
    Populates Flask `g.current_user_id` and `g.current_user_claims`.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            g.current_user_id = get_jwt_identity()
            g.current_user_claims = get_jwt()
        except JWTExtendedException as e:
            logger.warning(f"Unauthorized access attempt: {e}")
            return jsonify({
                "error": "unauthorized",
                "message": "Missing or invalid authorization token.",
            }), 401
        except Exception as e:
            logger.error(f"JWT verification error: {e}")
            return jsonify({
                "error": "unauthorized",
                "message": "Authentication failed.",
            }), 401

        return fn(*args, **kwargs)

    return wrapper


def require_admin(fn: Callable) -> Callable:
    """
    Decorator to restrict route access strictly to users with the 'admin' role.
    Returns 401 if not authenticated, 403 if authenticated but not an admin.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            claims = get_jwt()
            g.current_user_id = user_id
            g.current_user_claims = claims
        except JWTExtendedException as e:
            logger.warning(f"Admin route access attempt without valid JWT: {e}")
            return jsonify({
                "error": "unauthorized",
                "message": "Missing or invalid authorization token.",
            }), 401
        except Exception as e:
            logger.error(f"JWT verification error on admin route: {e}")
            return jsonify({
                "error": "unauthorized",
                "message": "Authentication failed.",
            }), 401

        role = claims.get("role", "").lower()
        if role != "admin":
            logger.warning(f"Forbidden access: User id={user_id} with role='{role}' attempted to access admin resource.")
            return jsonify({
                "error": "forbidden",
                "message": "Admin privileges required to access this resource.",
            }), 403

        return fn(*args, **kwargs)

    return wrapper
