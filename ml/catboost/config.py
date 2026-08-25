"""
ml/catboost/config.py — CatBoost Classifier configuration.

All hyperparameters are defined here.
No hardcoded values elsewhere in the ml/catboost/ module.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import os


@dataclass
class CatBoostConfig:
    # ── Model Training Hyperparameters ──────────────────────────────────────
    iterations: int = 500
    learning_rate: float = 0.05
    depth: int = 6
    loss_function: str = "Logloss"          # Binary classification
    eval_metric: str = "AUC"
    l2_leaf_reg: float = 3.0
    random_seed: int = 42
    early_stopping_rounds: int = 50

    # ── Feature Handling ────────────────────────────────────────────────────
    # Names of categorical features inside the feature vector
    cat_features: List[str] = field(default_factory=lambda: [
        "weather_risk_level",
        "landslide_severity",
    ])

    # ── Data Split ──────────────────────────────────────────────────────────
    test_size: float = 0.20        # 80/20 chronological split

    # ── Paths ────────────────────────────────────────────────────────────────
    checkpoint_dir: str = os.path.join(
        os.path.dirname(__file__), "checkpoints"
    )
    model_filename: str = "catboost_route_classifier.cbm"
    metrics_filename: str = "catboost_metrics.json"

    @property
    def model_path(self) -> str:
        return os.path.join(self.checkpoint_dir, self.model_filename)

    @property
    def metrics_path(self) -> str:
        return os.path.join(self.checkpoint_dir, self.metrics_filename)

    # ── Labelling Rule (documented) ─────────────────────────────────────────
    # Since real human route-choice labels are unavailable in the RouteIQ MVP,
    # we use a heuristic proxy label derived from the feature vector:
    #
    #   label = 1 (GOOD route) if ALL of the following hold:
    #     • TCI < 1.5            (travel time ≤ 150% of free-flow)
    #     • weather_risk_score < 0.4   (moderate or better weather)
    #     • road_blocked == 0    (no active landslide blockage)
    #     • event_impact_score < 0.5   (event congestion is manageable)
    #
    #   label = 0 (POOR route) otherwise.
    #
    # When real driver preference data is collected (Phase 15+), these labels
    # should be replaced with actual human choices.
    TCI_THRESHOLD: float = 1.5
    WEATHER_RISK_THRESHOLD: float = 0.4
    EVENT_IMPACT_THRESHOLD: float = 0.5

    def compute_label(self, feature_vector: dict) -> int:
        """Heuristic proxy label. See class-level docstring for the rule."""
        tci_ok = feature_vector.get("tci", 999.0) < self.TCI_THRESHOLD
        weather_ok = feature_vector.get("weather_risk_score", 1.0) < self.WEATHER_RISK_THRESHOLD
        not_blocked = feature_vector.get("road_blocked", 1) == 0
        events_ok = feature_vector.get("event_impact_score", 1.0) < self.EVENT_IMPACT_THRESHOLD
        return int(tci_ok and weather_ok and not_blocked and events_ok)
