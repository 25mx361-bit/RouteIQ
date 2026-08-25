"""
backend/models/user.py — User document model.

Collection: users

Schema
------
_id          : ObjectId  (auto)
name         : str       — display name
email        : str       — unique login identifier
password_hash: str       — bcrypt hash (never store plain-text)
role         : str       — "user" | "admin"  (default: "user")
is_active    : bool      — soft-enable/disable account
created_at   : datetime
updated_at   : datetime

Indexes (created in database.py)
---------------------------------
  email         UNIQUE ASCENDING
  created_at    DESCENDING
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from pymongo.database import Database

from backend.models.base import BaseModel


class UserModel(BaseModel):
    COLLECTION = "users"
    REQUIRED_FIELDS = ["name", "email", "password_hash"]

    # ------------------------------------------------------------------
    # Domain-specific helpers
    # ------------------------------------------------------------------

    @classmethod
    def find_by_email(cls, db: Database, email: str) -> Optional[Dict[str, Any]]:
        """Return user document for *email* (case-insensitive match)."""
        return db[cls.COLLECTION].find_one({"email": email.strip().lower()})

    @classmethod
    def insert(cls, db: Database, data: Dict[str, Any]):
        """Normalise email to lowercase before inserting."""
        data["email"] = data.get("email", "").strip().lower()
        data.setdefault("role", "user")
        data.setdefault("is_active", True)
        return super().insert(db, data)

    @classmethod
    def deactivate(cls, db: Database, doc_id: str):
        """Soft-delete: set is_active=False."""
        return cls.update(db, doc_id, {"is_active": False})

    @classmethod
    def set_role(cls, db: Database, doc_id: str, role: str):
        allowed = {"user", "admin"}
        if role not in allowed:
            raise ValueError(f"Role must be one of {allowed}")
        return cls.update(db, doc_id, {"role": role})
