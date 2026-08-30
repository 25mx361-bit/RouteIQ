"""
ml/patchtst/config.py — Configuration for PatchTST traffic forecasting model.
"""
import os
from dataclasses import dataclass
from pathlib import Path

# Base ML directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

@dataclass
class PatchTSTConfig:
    # Data params
    context_length: int = 96      # Lookback window (24 hours = 96 * 15m)
    forecast_horizon: int = 48    # Lookahead horizon (12 hours = 48 * 15m)
    stride: int = 8               # Sliding window step
    
    # Patching params
    patch_length: int = 16
    patch_stride: int = 8
    
    # Model architecture
    d_model: int = 128
    n_heads: int = 8
    n_encoder_layers: int = 3
    dropout: float = 0.2
    
    # Training params
    batch_size: int = 32
    learning_rate: float = 1e-4
    epochs: int = 20
    patience: int = 5
    
    # Paths
    checkpoints_dir: Path = BASE_DIR / "ml" / "patchtst" / "checkpoints"
    model_path: Path = checkpoints_dir / "patchtst_traffic.pth"
    metrics_path: Path = checkpoints_dir / "patchtst_metrics.json"
    scaler_path: Path = checkpoints_dir / "patchtst_scaler.pkl"

    def __post_init__(self):
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
