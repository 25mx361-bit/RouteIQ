"""
ml/patchtst/config.py — Configuration for PatchTST traffic forecasting model.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

# Base ML directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

@dataclass
class PatchTSTConfig:
    # Data params
    context_length: int = 96      # Lookback window (24 hours at 15-min intervals)
    forecast_horizon: int = 36    # Lookahead (9 hours → covers pre-event lookahead)
    stride: int = 2               # Dense sliding window step for maximum temporal sample diversity

    # Patching params
    patch_length: int = 16
    patch_stride: int = 8

    # Model architecture
    d_model: int = 128
    n_heads: int = 8
    n_encoder_layers: int = 3
    dropout: float = 0.1

    # Training params
    batch_size: int = 32
    learning_rate: float = 3e-4
    weight_decay: float = 1e-4
    epochs: int = 35
    patience: int = 10            # Early stopping patience

    # Split ratios (chronological)
    train_pct: float = 0.70
    val_pct: float = 0.15
    # test_pct implicitly = 1 - train_pct - val_pct = 0.15

    # Feature configuration
    num_features: int = 12        # Input feature count (FEATURE_COLUMNS_ENRICHED)
    num_target_features: int = 3  # speed_kmh, current_travel_time, tci

    # Version
    model_version: str = "PatchTST_v2"

    # Paths
    checkpoints_dir: Path = BASE_DIR / "ml" / "patchtst" / "checkpoints"
    model_path: Path = checkpoints_dir / "patchtst_traffic_v2.pth"
    metrics_path: Path = checkpoints_dir / "patchtst_metrics.json"
    scaler_path: Path = checkpoints_dir / "patchtst_scaler_v2.pkl"
    registry_path: Path = checkpoints_dir / "model_registry.json"

    # Legacy paths (v1 — kept for backward compat)
    legacy_model_path: Path = checkpoints_dir / "patchtst_traffic.pth"
    legacy_scaler_path: Path = checkpoints_dir / "patchtst_scaler.pkl"

    def __post_init__(self):
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
