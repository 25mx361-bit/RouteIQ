"""
tests/test_ml.py — ML Model unit tests (PatchTST preprocessing, dataset, forward pass; CatBoost features).

Tests:
  1. clean_traffic_df — removes zero/negative speeds, clips outliers, drops duplicates
  2. add_time_features — hour_sin/cos range, is_weekend correct
  3. add_derived_features — TCI = current / free_flow, clamped
  4. fill_missing_weather — fills missing columns with defaults
  5. chronological_split — 70/15/15 ratio, no shuffle (order preserved)
  6. TrafficDataset — correct sliding window count
  7. PatchTST forward pass — output shape = (batch, pred_len, num_features)
  8. CatBoost feature list — all required features present
  9. CatBoost prediction — returns float in [0, 1]
"""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ---------------------------------------------------------------------------
# PatchTST Preprocessing
# ---------------------------------------------------------------------------

from ml.patchtst.preprocessing import (
    clean_traffic_df,
    add_time_features,
    add_derived_features,
    fill_missing_weather,
    chronological_split,
    FEATURE_COLUMNS_ENRICHED,
)


def _make_traffic_df(n=200, seed=42):
    """Create a minimal valid traffic DataFrame."""
    rng = np.random.default_rng(seed)
    now = datetime(2026, 9, 1, 0, 0, 0, tzinfo=timezone.utc)
    timestamps = [now + timedelta(minutes=15 * i) for i in range(n)]
    return pd.DataFrame({
        "timestamp": timestamps,
        "segment_id": "seg_test",
        "speed_kmh": rng.uniform(10, 60, n),
        "free_flow_speed": rng.uniform(50, 60, n),
        "current_travel_time": rng.uniform(300, 900, n),
        "free_flow_travel_time": rng.uniform(200, 400, n),
        "temperature": rng.uniform(24, 35, n),
        "precipitation": rng.uniform(0, 2, n),
        "humidity": rng.uniform(55, 80, n),
        "wind_speed": rng.uniform(5, 20, n),
    })


# 1. clean_traffic_df — zero speeds removed, clipping applied
def test_clean_traffic_df_removes_zero_speed():
    df = _make_traffic_df(100)
    df.loc[0, "speed_kmh"] = 0.0     # should be removed
    df.loc[1, "speed_kmh"] = -5.0    # should be removed
    df.loc[2, "speed_kmh"] = 200.0   # should be clipped to 120
    cleaned = clean_traffic_df(df)
    assert (cleaned["speed_kmh"] > 0).all(), "All cleaned speeds must be > 0"
    assert cleaned["speed_kmh"].max() <= 120.0, "Speed must be clipped to 120 km/h"
    assert len(cleaned) < 100, "Rows with zero/negative speed should be removed"


def test_clean_traffic_df_removes_duplicates():
    df = _make_traffic_df(50)
    # Duplicate the first row (same segment_id + timestamp)
    dup = df.iloc[[0]].copy()
    df = pd.concat([df, dup], ignore_index=True)
    cleaned = clean_traffic_df(df)
    assert cleaned.duplicated(subset=["segment_id", "timestamp"]).sum() == 0, \
        "No duplicate (segment_id, timestamp) pairs should remain"


# 2. add_time_features — valid hour_sin/cos, is_weekend
def test_add_time_features_sin_cos_range():
    df = _make_traffic_df(48)
    df = add_time_features(df)
    assert "hour_sin" in df.columns and "hour_cos" in df.columns
    assert df["hour_sin"].between(-1.0, 1.0).all(), "hour_sin must be in [-1, 1]"
    assert df["hour_cos"].between(-1.0, 1.0).all(), "hour_cos must be in [-1, 1]"


def test_add_time_features_is_weekend():
    # Create timestamps on a known weekend (2026-10-03 is Saturday)
    sat = datetime(2026, 10, 3, 10, 0, 0, tzinfo=timezone.utc)
    mon = datetime(2026, 10, 5, 10, 0, 0, tzinfo=timezone.utc)
    df = pd.DataFrame({
        "timestamp": [sat, mon],
        "segment_id": "s",
        "speed_kmh": [30.0, 30.0],
        "free_flow_speed": [50.0, 50.0],
        "current_travel_time": [300.0, 300.0],
        "free_flow_travel_time": [200.0, 200.0],
    })
    df = add_time_features(df)
    assert df.loc[df["timestamp"] == sat, "is_weekend"].values[0] == 1, "Saturday must be weekend"
    assert df.loc[df["timestamp"] == mon, "is_weekend"].values[0] == 0, "Monday must be weekday"


# 3. add_derived_features — TCI formula and clamping
def test_add_derived_features_tci_formula():
    df = pd.DataFrame({
        "timestamp": [datetime(2026, 9, 1, tzinfo=timezone.utc)] * 3,
        "segment_id": "s",
        "speed_kmh": [30.0, 30.0, 30.0],
        "free_flow_speed": [50.0, 50.0, 50.0],
        "current_travel_time": [600.0, 300.0, 60.0],
        "free_flow_travel_time": [300.0, 300.0, 300.0],
    })
    df = add_derived_features(df)
    assert "tci" in df.columns
    assert df.loc[0, "tci"] == pytest.approx(2.0, abs=0.01), "TCI = 600/300 = 2.0"
    assert df.loc[1, "tci"] == pytest.approx(1.0, abs=0.01), "TCI = 300/300 = 1.0"
    # TCI of 60/300 = 0.2 — clamped to 0.5
    assert df.loc[2, "tci"] >= 0.5, "TCI must be clamped to minimum 0.5"


def test_add_derived_features_tci_max_clamp():
    df = pd.DataFrame({
        "timestamp": [datetime(2026, 9, 1, tzinfo=timezone.utc)],
        "segment_id": "s",
        "speed_kmh": [5.0],
        "free_flow_speed": [50.0],
        "current_travel_time": [9000.0],    # very high
        "free_flow_travel_time": [300.0],   # TCI = 30 → clamped to 10
    })
    df = add_derived_features(df)
    assert df.loc[0, "tci"] <= 10.0, "TCI must be clamped to maximum 10.0"


# 4. fill_missing_weather — defaults applied
def test_fill_missing_weather_defaults():
    df = pd.DataFrame({
        "timestamp": [datetime(2026, 9, 1, tzinfo=timezone.utc)],
        "segment_id": "s",
        "speed_kmh": [30.0],
        "current_travel_time": [300.0],
        "free_flow_travel_time": [200.0],
        "free_flow_speed": [50.0],
        # No weather columns
    })
    df = fill_missing_weather(df)
    assert "temperature" in df.columns and df["temperature"].iloc[0] == 28.0
    assert "precipitation" in df.columns and df["precipitation"].iloc[0] == 0.0
    assert "humidity" in df.columns and df["humidity"].iloc[0] == 65.0
    assert "wind_speed" in df.columns and df["wind_speed"].iloc[0] == 10.0


# 5. chronological_split — ratio and order preserved
def test_chronological_split_ratios():
    df = _make_traffic_df(200)
    df = df.sort_values("timestamp").reset_index(drop=True)
    train, val, test = chronological_split(df, train_pct=0.70, val_pct=0.15)

    total = len(df)
    assert len(train) == int(total * 0.70)
    assert len(val) == int(total * 0.15)
    assert len(train) + len(val) + len(test) == total


def test_chronological_split_preserves_order():
    df = _make_traffic_df(100)
    df = df.sort_values("timestamp").reset_index(drop=True)
    train, val, test = chronological_split(df, train_pct=0.70, val_pct=0.15)
    # Last timestamp in train < first timestamp in val
    assert train["timestamp"].max() <= val["timestamp"].min(), "Train/val must be chronologically ordered"
    assert val["timestamp"].max() <= test["timestamp"].min(), "Val/test must be chronologically ordered"


# ---------------------------------------------------------------------------
# PatchTST Dataset & Forward Pass
# ---------------------------------------------------------------------------

def test_traffic_dataset_window_count():
    from ml.patchtst.config import PatchTSTConfig
    from ml.patchtst.dataset import TrafficDataset

    config = PatchTSTConfig()
    config.context_length = 32
    config.forecast_horizon = 8
    config.stride = 4

    n = 100
    data = np.random.randn(n, 12).astype(np.float32)
    dataset = TrafficDataset(data, config, target_indices=[0, 1, 2])

    expected_windows = max(0, (n - config.context_length - config.forecast_horizon) // config.stride + 1)
    assert len(dataset) == expected_windows, (
        f"Expected {expected_windows} windows, got {len(dataset)}"
    )


def test_patchtst_forward_pass_output_shape():
    """Model must accept (batch, context_length, num_features) and output (batch, pred_len, num_features)."""
    import torch
    from ml.patchtst.config import PatchTSTConfig
    from ml.patchtst.model import PatchTST

    config = PatchTSTConfig()
    config.context_length = 32
    config.forecast_horizon = 8
    config.d_model = 32
    config.n_heads = 2
    config.n_encoder_layers = 1
    config.patch_length = 8
    config.patch_stride = 4

    num_features = 6
    model = PatchTST(config, num_features=num_features)
    model.eval()

    batch_size = 4
    x = torch.randn(batch_size, config.context_length, num_features)
    with torch.no_grad():
        out = model(x)

    assert out.shape[0] == batch_size, "Batch dimension must match input"
    assert out.shape[1] == config.forecast_horizon, f"Output pred_len must be {config.forecast_horizon}"
    assert out.shape[2] == num_features, f"Output feature dim must be {num_features}"


# ---------------------------------------------------------------------------
# CatBoost Features & Prediction
# ---------------------------------------------------------------------------

def test_catboost_feature_list_complete():
    """All required features must be present in the CatBoost feature definition."""
    from ml.catboost.features import CATBOOST_FEATURE_COLUMNS

    required = [
        "tci", "weather_risk_score", "distance_km", "duration_min",
        "road_blocked", "landslide_active",
    ]
    for feat in required:
        assert feat in CATBOOST_FEATURE_COLUMNS, (
            f"Required feature '{feat}' missing from CATBOOST_FEATURE_COLUMNS"
        )


def test_catboost_prediction_returns_valid_score():
    """CatBoost inference must return a float in [0, 1] without raising."""
    from unittest.mock import patch, MagicMock
    import numpy as np

    # Mock the CatBoost model to avoid needing a real trained .cbm file
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([[0.85]])

    with patch("ml.catboost.prediction.load_model", return_value=mock_model):
        from ml.catboost.prediction import predict_route_score

        feature_vector = {
            "tci": 1.2,
            "weather_risk_score": 0.1,
            "distance_km": 5.0,
            "duration_min": 12.0,
            "road_blocked": 0,
            "landslide_active": 0,
            "landslide_severity": "NONE",
            "event_impact_score": 0.0,
            "hour": 9,
            "day_of_week": 1,
            "is_weekend": 0,
            "is_peak_hour": 1,
            "predicted_speed_kmh": 36.0,
        }
        score = predict_route_score(feature_vector)

    assert isinstance(score, (float, int, np.floating)), f"Score must be numeric, got {type(score)}"
    assert 0.0 <= float(score) <= 1.0, f"CatBoost score must be in [0, 1], got {score}"
