"""
backend/repositories/base_repository.py — Generic Repository Base Class for PyMongo.

Provides clean CRUD operations backed by a specific Model and Database instance.
No ORM/ODM used — pure PyMongo operations.
"""
from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from bson import ObjectId
from pymongo.database import Database
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from backend.database import get_db
from backend.models.base import BaseModel

M = TypeVar("M", bound=BaseModel)


class BaseRepository(Generic[M]):
    """Generic repository handling standard CRUD operations with PyMongo."""

    model: Type[M]

    def __init__(self, db: Optional[Database] = None):
        self._db = db

    @property
    def db(self) -> Database:
        if self._db is not None:
            return self._db
        return get_db()

    def create(self, data: Dict[str, Any]) -> str:
        """Insert a document and return its string ID."""
        result: InsertOneResult = self.model.insert(self.db, data)
        return str(result.inserted_id)

    def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single document by string ObjectId."""
        doc = self.model.find_by_id(self.db, doc_id)
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve the first matching document."""
        doc = self.model.find_one(self.db, query)
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def find(
        self,
        query: Optional[Dict[str, Any]] = None,
        sort: Optional[List] = None,
        limit: int = 0,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        """Query multiple documents and convert ObjectId to string."""
        docs = self.model.find_many(
            self.db, query or {}, sort=sort, limit=limit, skip=skip
        )
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return docs

    def update(self, doc_id: str, update_data: Dict[str, Any]) -> bool:
        """Update fields on document and return True if modified or matched."""
        result: UpdateResult = self.model.update(self.db, doc_id, update_data)
        return result.matched_count > 0

    def delete(self, doc_id: str) -> bool:
        """Delete document by ID and return True if deleted."""
        result: DeleteResult = self.model.delete(self.db, doc_id)
        return result.deleted_count > 0

    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        return self.model.count(self.db, query)
