"""
backend/models/model_logs.py — Machine Learning Training & Inference Logs model.

Collection: model_logs

Schema
------
_id             : ObjectId
model_name      : str — "PatchTST" | "CatBoost"
run_type        : str — "training" | "inference" | "evaluation"
version         : str — model version / checkpoint tag
metrics         : dict — e.g. {"mae": 2.14, "rmse": 3.82, "accuracy": 0.89}
parameters      : dict — hyperparameters or input dimensions
dataset_info    : dict — samples_count, date_range
logged_at       : datetime
status          : str — "SUCCESS" | "FAILED" | "IN_PROGRESS"
notes           : str
created_at      : datetime
updated_at      : datetime

Indexes (created in database.py)
---------------------------------
  model_name    ASCENDING
  logged_at     DESCENDING
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pymongo.database import Database
from pymongo import DESCENDING

from backend.models.base import BaseModel


class ModelLogModel(BaseModel):
    COLLECTION = "model_logs"
    REQUIRED_FIELDS = ["model_name", "run_type", "status"]

    @classmethod
    def insert(cls, db: Database, data: Dict[str, Any]):
        now = cls.utcnow()
        data.setdefault("logged_at", now)
        data.setdefault("metrics", {})
        data.setdefault("parameters", {})
        return super().insert(db, data)

    @classmethod
    def find_latest_by_model(
        cls, db: Database, model_name: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        return cls.find_many(
            db,
            {"model_name": model_name},
            sort=[("logged_at", DESCENDING)],
            limit=limit,
        )
