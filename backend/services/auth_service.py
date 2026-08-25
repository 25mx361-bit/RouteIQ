"""
backend/services/auth_service.py — Authentication & Role Service.

Handles:
  - Password hashing with bcrypt
  - User registration & duplicate email check
  - User authentication & credential validation
  - JWT token generation with role & identity claims
  - User profile retrieval
"""
from __future__ import annotations

from typing import Any, Dict, Optional
import bcrypt
from flask_jwt_extended import create_access_token
from loguru import logger

from backend.repositories.user_repository import UserRepository


class AuthError(Exception):
    """Base exception for authentication errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class DuplicateEmailError(AuthError):
    def __init__(self, message: str = "An account with this email already exists."):
        super().__init__(message, status_code=409)


class InvalidCredentialsError(AuthError):
    def __init__(self, message: str = "Invalid email or password."):
        super().__init__(message, status_code=401)


class UserNotFoundError(AuthError):
    def __init__(self, message: str = "User not found."):
        super().__init__(message, status_code=404)


class ValidationError(AuthError):
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class AuthService:
    def __init__(self, user_repo: Optional[UserRepository] = None):
        self.user_repo = user_repo or UserRepository()

    def register(
        self,
        name: str,
        email: str,
        password: str,
        role: str = "user",
    ) -> Dict[str, Any]:
        """
        Register a new user, hash password, check duplicate, and return access token.
        """
        name = name.strip() if name else ""
        email = email.strip().lower() if email else ""

        if not name:
            raise ValidationError("Name is required.")
        if not email or "@" not in email or "." not in email:
            raise ValidationError("A valid email address is required.")
        if not password or len(password) < 8:
            raise ValidationError("Password must be at least 8 characters.")

        role_normalized = role.strip().lower()
        if role_normalized not in ("user", "admin"):
            role_normalized = "user"

        # Check for existing email
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            logger.warning(f"Registration conflict: email already registered -> {email}")
            raise DuplicateEmailError()

        # Hash password with bcrypt
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

        user_data = {
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "role": role_normalized,
            "is_active": True,
        }

        user_id = self.user_repo.create(user_data)
        logger.info(f"User registered successfully: id={user_id}, email={email}, role={role_normalized}")

        # Issue JWT
        token = self._generate_token(user_id, email, name, role_normalized)

        return {
            "message": "User registered successfully.",
            "access_token": token,
            "token_type": "Bearer",
            "user": {
                "id": user_id,
                "name": name,
                "email": email,
                "role": role_normalized,
            },
        }

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password and issue JWT token.
        """
        email = email.strip().lower() if email else ""
        if not email or not password:
            raise ValidationError("Email and password are required.")

        user = self.user_repo.get_by_email(email)
        if not user:
            logger.warning(f"Login failed: User not found for email -> {email}")
            raise InvalidCredentialsError()

        if not user.get("is_active", True):
            raise AuthError("Account has been deactivated. Please contact support.", status_code=403)

        # Verify password hash
        stored_hash = user.get("password_hash", "")
        if not stored_hash or not bcrypt.checkpw(
            password.encode("utf-8"), stored_hash.encode("utf-8")
        ):
            logger.warning(f"Login failed: Incorrect password for email -> {email}")
            raise InvalidCredentialsError()

        user_id = str(user["_id"])
        user_role = user.get("role", "user").lower()
        user_name = user.get("name", "")

        token = self._generate_token(user_id, email, user_name, user_role)
        logger.info(f"User logged in successfully: id={user_id}, email={email}")

        return {
            "message": "Login successful.",
            "access_token": token,
            "token_type": "Bearer",
            "user": {
                "id": user_id,
                "name": user_name,
                "email": email,
                "role": user_role,
            },
        }

    def logout(self) -> Dict[str, Any]:
        """
        Logout user (for stateless JWT, signals frontend to clear token).
        """
        return {"message": "Logged out successfully."}

    def get_current_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Fetch user details excluding sensitive password hash.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        user.pop("password_hash", None)
        return user

    def _generate_token(
        self, user_id: str, email: str, name: str, role: str
    ) -> str:
        """Create JWT access token with role and user claims."""
        additional_claims = {
            "role": role,
            "email": email,
            "name": name,
        }
        return create_access_token(
            identity=user_id,
            additional_claims=additional_claims,
        )
