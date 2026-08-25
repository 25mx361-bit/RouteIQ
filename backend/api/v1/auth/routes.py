"""
auth/routes.py — Authentication Blueprint
==========================================
Endpoints:
  POST /api/v1/auth/register  — Create new user account
  POST /api/v1/auth/login     — Issue JWT access token
  GET  /api/v1/auth/me        — Return current user profile (protected)
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
import bcrypt
from loguru import logger

from backend.extensions import mongo

auth_bp = Blueprint("auth", __name__)


# ---------------------------------------------------------------------------
# POST /api/v1/auth/register
# ---------------------------------------------------------------------------
@auth_bp.post("/register")
def register():
    """Register a new user."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "invalid_json", "message": "Request body must be JSON."}), 400

    name     = data.get("name", "").strip()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # --- Validate required fields ---
    if not name or not email or not password:
        return jsonify({"error": "missing_fields", "message": "name, email, and password are required."}), 422

    if len(password) < 8:
        return jsonify({"error": "weak_password", "message": "Password must be at least 8 characters."}), 422

    # --- Check for duplicate email ---
    existing = mongo.db.users.find_one({"email": email})
    if existing:
        return jsonify({"error": "email_exists", "message": "An account with this email already exists."}), 409

    # --- Hash password ---
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # --- Persist user ---
    user_doc = {
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "role": "user",
    }
    result = mongo.db.users.insert_one(user_doc)

    logger.info(f"New user registered: {email}")
    return jsonify({
        "message": "Registration successful.",
        "user_id": str(result.inserted_id),
    }), 201


# ---------------------------------------------------------------------------
# POST /api/v1/auth/login
# ---------------------------------------------------------------------------
@auth_bp.post("/login")
def login():
    """Authenticate user and return a JWT access token."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "invalid_json", "message": "Request body must be JSON."}), 400

    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "missing_fields", "message": "email and password are required."}), 422

    user = mongo.db.users.find_one({"email": email})
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return jsonify({"error": "invalid_credentials", "message": "Incorrect email or password."}), 401

    access_token = create_access_token(identity=str(user["_id"]))

    logger.info(f"User logged in: {email}")
    return jsonify({
        "access_token": access_token,
        "token_type": "Bearer",
        "user": {"id": str(user["_id"]), "name": user["name"], "email": user["email"]},
    }), 200


# ---------------------------------------------------------------------------
# GET /api/v1/auth/me
# ---------------------------------------------------------------------------
@auth_bp.get("/me")
@jwt_required()
def me():
    """Return the authenticated user's profile."""
    user_id = get_jwt_identity()
    from bson import ObjectId
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
    if not user:
        return jsonify({"error": "not_found", "message": "User not found."}), 404

    user["_id"] = str(user["_id"])
    return jsonify({"user": user}), 200
