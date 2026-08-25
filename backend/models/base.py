"""
backend/models/base.py — Shared base class for all RouteIQ document models.

Every model inherits BaseModel which provides:
  - Schema definition (REQUIRED_FIELDS, OPTIONAL_FIELDS)
  - Validation via validate()
  - Static CRUD helpers: find_by_id, insert, update, delete
  - Automatic created_at / updated_at timestamp injection

All methods accept a `db` parameter (pymongo.database.Database) so they
can be used both inside Flask context and in standalone scripts/tests.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.database import Database
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult


class BaseModel:
    """
    Abstract base for RouteIQ MongoDB document models.

    Subclasses must define:
        COLLECTION: str   — the MongoDB collection name
        REQUIRED_FIELDS: list[str]  — fields that must be present on insert
    """

    COLLECTION: str = ""
    REQUIRED_FIELDS: list[str] = []

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @classmethod
    def validate(cls, data: Dict[str, Any]) -> None:
        """
        Raise ValueError if any required field is missing from *data*.
        """
        missing = [f for f in cls.REQUIRED_FIELDS if f not in data or data[f] is None]
        if missing:
            raise ValueError(
                f"[{cls.__name__}] Missing required fields: {missing}"
            )

    # ------------------------------------------------------------------
    # Timestamp helpers
    # ------------------------------------------------------------------

    @staticmethod
    def utcnow() -> datetime:
        return datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # CRUD statics
    # ------------------------------------------------------------------

    @classmethod
    def insert(cls, db: Database, data: Dict[str, Any]) -> InsertOneResult:
        """Validate, inject timestamps, and insert one document."""
        cls.validate(data)
        now = cls.utcnow()
        data.setdefault("created_at", now)
        data.setdefault("updated_at", now)
        return db[cls.COLLECTION].insert_one(data)

    @classmethod
    def find_by_id(cls, db: Database, doc_id: str) -> Optional[Dict[str, Any]]:
        """Return a single document by its _id string, or None."""
        try:
            oid = ObjectId(doc_id)
        except (InvalidId, TypeError):
            return None
        return db[cls.COLLECTION].find_one({"_id": oid})

    @classmethod
    def find_one(cls, db: Database, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Return the first document matching *query*, or None."""
        return db[cls.COLLECTION].find_one(query)

    @classmethod
    def find_many(
        cls,
        db: Database,
        query: Dict[str, Any],
        *,
        sort: Optional[List] = None,
        limit: int = 0,
        skip: int = 0,
        projection: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """Return all documents matching *query* as a list."""
        cursor = db[cls.COLLECTION].find(query, projection)
        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    @classmethod
    def update(
        cls, db: Database, doc_id: str, update_data: Dict[str, Any]
    ) -> UpdateResult:
        """$set update_data on the document identified by *doc_id*."""
        update_data["updated_at"] = cls.utcnow()
        return db[cls.COLLECTION].update_one(
            {"_id": ObjectId(doc_id)}, {"$set": update_data}
        )

    @classmethod
    def delete(cls, db: Database, doc_id: str) -> DeleteResult:
        """Hard-delete the document identified by *doc_id*."""
        return db[cls.COLLECTION].delete_one({"_id": ObjectId(doc_id)})

    @classmethod
    def count(cls, db: Database, query: Optional[Dict] = None) -> int:
        """Return the count of documents matching *query* (default: all)."""
        return db[cls.COLLECTION].count_documents(query or {})
