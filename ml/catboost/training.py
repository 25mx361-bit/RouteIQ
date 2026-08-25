"""
ml/catboost/training.py — CatBoost training pipeline for RouteIQ.

Data Source
-----------
Historical route feature vectors are loaded from the MongoDB ``predictions``
collection (written by the routing pipeline after each route search).

Labelling Rule (Proxy Labels — documented)
------------------------------------------
Since real human route-choice labels are not yet available, we generate
heuristic proxy labels using CatBoostConfig.compute_label():

    label = 1 (GOOD route) if:
        TCI < 1.5  AND  weather_risk_score < 0.4
        AND road_blocked == 0  AND event_impact_score < 0.5

    label = 0 (POOR route) otherwise.

When real driver preference data is available (Phase 15+), replace this
labelling step with actual feedback signals.

Split Strategy
--------------
Chronological 80/20 split — NOT random shuffle — to prevent temporal leakage.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from catboost import CatBoostClassifier, Pool

from ml.catboost.config import CatBoostConfig
from ml.catboost.features import ALL_FEATURES, CAT_FEATURE_INDICES, CATEGORICAL_FEATURES, TARGET_COLUMN
from ml.catboost.evaluation import compute_metrics

logger = logging.getLogger(__name__)


# ── Data Loading ─────────────────────────────────────────────────────────────

def load_training_data(db) -> pd.DataFrame:
    """
    Load route feature vectors from MongoDB ``predictions`` collection.
    Each document must have a ``features`` subdoc produced by
    feature_engineering_service.build_route_feature_vector().

    Returns a DataFrame with ALL_FEATURES columns + TARGET_COLUMN.
    """
    collection = db["predictions"]
    cursor = collection.find(
        {"features": {"$exists": True}},
        sort=[("created_at", 1)],          # Ascending — chronological order
    )

    records = []
    cfg = CatBoostConfig()

    for doc in cursor:
        fv: Dict[str, Any] = doc.get("features", {})
        if not fv:
            continue
        # Skip records with missing essential keys
        if any(k not in fv for k in ["tci", "road_blocked", "weather_risk_score"]):
            continue

        row = {col: fv.get(col, 0) for col in ALL_FEATURES}
        # Ensure categoricals are strings (CatBoost requirement)
        for cat in CATEGORICAL_FEATURES:
            row[cat] = str(row.get(cat, "UNKNOWN") or "UNKNOWN")

        row[TARGET_COLUMN] = cfg.compute_label(fv)
        records.append(row)

    if not records:
        logger.warning("No training records found in MongoDB 'predictions' collection.")
        return pd.DataFrame()

    df = pd.DataFrame(records)
    logger.info(f"Loaded {len(df)} training records. Label distribution:\n{df[TARGET_COLUMN].value_counts().to_dict()}")
    return df


# ── Train / Validation Split ──────────────────────────────────────────────────

def chronological_split(
    df: pd.DataFrame,
    test_size: float = 0.20,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Chronological (time-ordered) train/val split.
    Assumes df is already sorted by created_at (ascending).
    """
    split_idx = int(len(df) * (1.0 - test_size))
    train_df = df.iloc[:split_idx].copy()
    val_df = df.iloc[split_idx:].copy()
    logger.info(f"Train size: {len(train_df)} | Val size: {len(val_df)}")
    return train_df, val_df


# ── CatBoost Pool Builder ─────────────────────────────────────────────────────

def _build_pool(df: pd.DataFrame) -> Pool:
    X = df[ALL_FEATURES]
    y = df[TARGET_COLUMN]
    return Pool(
        data=X,
        label=y,
        cat_features=CAT_FEATURE_INDICES,
        feature_names=ALL_FEATURES,
    )


# ── Training Entry Point ──────────────────────────────────────────────────────

def train_catboost(
    db,
    config: Optional[CatBoostConfig] = None,
) -> Dict[str, Any]:
    """
    Full training pipeline.

    Args:
        db:     pymongo Database instance.
        config: CatBoostConfig (uses defaults if None).

    Returns:
        dict with keys: status, model_path, metrics, n_train, n_val.
    """
    cfg = config or CatBoostConfig()
    os.makedirs(cfg.checkpoint_dir, exist_ok=True)

    # 1. Load data
    df = load_training_data(db)
    if df.empty or len(df) < 10:
        return {
            "status": "error",
            "message": f"Insufficient training data ({len(df)} records). Need at least 10.",
        }

    # 2. Chronological split
    train_df, val_df = chronological_split(df, test_size=cfg.test_size)

    # 3. Build CatBoost Pools
    train_pool = _build_pool(train_df)
    val_pool = _build_pool(val_df)

    # 4. Build and train model
    model = CatBoostClassifier(
        iterations=cfg.iterations,
        learning_rate=cfg.learning_rate,
        depth=cfg.depth,
        loss_function=cfg.loss_function,
        eval_metric=cfg.eval_metric,
        l2_leaf_reg=cfg.l2_leaf_reg,
        random_seed=cfg.random_seed,
        early_stopping_rounds=cfg.early_stopping_rounds,
        verbose=100,
        cat_features=CATEGORICAL_FEATURES,
    )

    logger.info(f"Starting CatBoost training — {len(train_df)} train / {len(val_df)} val samples...")
    model.fit(
        train_pool,
        eval_set=val_pool,
        use_best_model=True,
    )

    # 5. Save checkpoint
    model.save_model(cfg.model_path)
    logger.info(f"Model saved to {cfg.model_path}")

    # 6. Evaluate on val set
    metrics = compute_metrics(model, val_pool, val_df[TARGET_COLUMN].tolist())

    # 7. Persist metrics to JSON
    metrics_payload = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_train": len(train_df),
        "n_val": len(val_df),
        "label_distribution_train": train_df[TARGET_COLUMN].value_counts().to_dict(),
        "labelling_rule": (
            "label=1 if TCI<1.5 AND weather_risk_score<0.4 "
            "AND road_blocked==0 AND event_impact_score<0.5"
        ),
        **metrics,
    }
    with open(cfg.metrics_path, "w") as f:
        json.dump(metrics_payload, f, indent=2, default=str)

    logger.info(f"Training complete. Metrics: {metrics}")
    return {
        "status": "success",
        "model_path": cfg.model_path,
        "metrics": metrics_payload,
        "n_train": len(train_df),
        "n_val": len(val_df),
    }
