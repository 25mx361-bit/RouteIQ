"""
ml/catboost/prediction.py — CatBoost inference for route suitability scoring.

Loads the best saved checkpoint and returns a suitability score for each
candidate route feature vector.

IMPORTANT — Safety filtering (BLOCKED routes) is NOT done here.
It is enforced upstream in backend/services/recommendation_service.py
BEFORE these scores are ever consulted.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import pandas as pd
from catboost import CatBoostClassifier, Pool

from ml.catboost.config import CatBoostConfig
from ml.catboost.features import ALL_FEATURES, CAT_FEATURE_INDICES, CATEGORICAL_FEATURES

logger = logging.getLogger(__name__)

# Module-level singleton (loaded once, reused)
_model_cache: Optional[CatBoostClassifier] = None
_loaded_model_path: Optional[str] = None


def load_model(config: Optional[CatBoostConfig] = None) -> CatBoostClassifier:
    """
    Load the CatBoost model from the checkpoint directory.
    Caches the model in memory to avoid repeated disk I/O.
    """
    global _model_cache, _loaded_model_path
    cfg = config or CatBoostConfig()

    if not os.path.exists(cfg.model_path):
        raise FileNotFoundError(
            f"CatBoost model checkpoint not found at '{cfg.model_path}'. "
            "Please trigger training first via POST /api/admin/models/catboost/train."
        )

    # Reload if the file has changed (e.g., after re-training)
    if _model_cache is None or _loaded_model_path != cfg.model_path:
        logger.info(f"Loading CatBoost model from {cfg.model_path}")
        _model_cache = CatBoostClassifier()
        _model_cache.load_model(cfg.model_path)
        _loaded_model_path = cfg.model_path
        logger.info("CatBoost model loaded successfully.")

    return _model_cache


def predict_route_scores(
    feature_vectors: List[Dict[str, Any]],
    config: Optional[CatBoostConfig] = None,
) -> List[Dict[str, Any]]:
    """
    Predict suitability scores for a list of route feature vectors.

    Args:
        feature_vectors: List of dicts produced by build_route_feature_vector().
        config:          CatBoostConfig (uses defaults if None).

    Returns:
        List of dicts, each with:
            score:       float in [0, 1] — probability of being a GOOD route.
            label:       int  — predicted class (1=good, 0=poor).
            route_index: int  — index in the input list.
    """
    if not feature_vectors:
        return []

    cfg = config or CatBoostConfig()
    model = load_model(cfg)

    # Build DataFrame in the correct column order
    rows = []
    for fv in feature_vectors:
        row = {col: fv.get(col, 0) for col in ALL_FEATURES}
        for cat in CATEGORICAL_FEATURES:
            row[cat] = str(row.get(cat, "UNKNOWN") or "UNKNOWN")
        rows.append(row)

    df = pd.DataFrame(rows, columns=ALL_FEATURES)
    pool = Pool(
        data=df,
        cat_features=CAT_FEATURE_INDICES,
        feature_names=ALL_FEATURES,
    )

    probas = model.predict_proba(pool)[:, 1]   # P(label=1 = GOOD route)
    labels = model.predict(pool)

    results = []
    for idx, (score, label) in enumerate(zip(probas, labels)):
        results.append({
            "route_index": idx,
            "score": round(float(score), 4),
            "label": int(label),
        })

    return results


def invalidate_cache() -> None:
    """Call this after re-training to force the next inference to reload the model."""
    global _model_cache, _loaded_model_path
    _model_cache = None
    _loaded_model_path = None
    logger.info("CatBoost model cache invalidated.")
