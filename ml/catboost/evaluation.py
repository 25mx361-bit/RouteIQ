"""
ml/catboost/evaluation.py — Model evaluation metrics.

Computes Accuracy, F1, and AUC on the held-out validation/test set.
Returns real numbers computed from the model — no synthetic values.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from catboost import CatBoostClassifier, Pool

logger = logging.getLogger(__name__)


def compute_metrics(
    model: CatBoostClassifier,
    pool: Pool,
    y_true: List[int],
) -> Dict[str, Any]:
    """
    Compute Accuracy, F1 (binary), and AUC on the given pool.

    Args:
        model:  Trained CatBoostClassifier.
        pool:   CatBoost Pool (with features + labels).
        y_true: Ground truth label list (0 or 1).

    Returns:
        dict with accuracy, f1, auc, n_samples.
    """
    try:
        from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
    except ImportError:
        logger.error("scikit-learn not installed. Run: pip install scikit-learn")
        return {"error": "scikit-learn not installed"}

    if not y_true:
        return {"error": "Empty validation set — cannot compute metrics"}

    # Predicted class labels and probabilities
    y_pred = model.predict(pool)
    y_prob = model.predict_proba(pool)[:, 1]  # P(label=1)

    acc = round(float(accuracy_score(y_true, y_pred)), 4)
    f1 = round(float(f1_score(y_true, y_pred, zero_division=0)), 4)

    # AUC requires both classes present in y_true
    try:
        auc = round(float(roc_auc_score(y_true, y_prob)), 4)
    except ValueError as e:
        logger.warning(f"AUC could not be computed (likely single class in val set): {e}")
        auc = None

    metrics = {
        "accuracy": acc,
        "f1": f1,
        "auc": auc,
        "n_samples": len(y_true),
    }
    logger.info(f"Evaluation — Accuracy: {acc}, F1: {f1}, AUC: {auc} (n={len(y_true)})")
    return metrics
