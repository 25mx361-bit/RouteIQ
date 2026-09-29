"""
ml/patchtst/dataset.py — PyTorch Dataset for PatchTST traffic forecasting.
Uses enriched 12-feature set. Supports explicit data_source labeling.
Synthetic data is clearly separated from real API observations.
"""
import numpy as np
import torch
from torch.utils.data import Dataset
import pandas as pd
import pickle
from pathlib import Path
from loguru import logger

from ml.patchtst.preprocessing import (
    FEATURE_COLUMNS_ENRICHED,
    TARGET_COLUMNS,
    build_feature_matrix,
    chronological_split,
)
from ml.patchtst.data_enrichment import load_and_enrich_from_mongo


def load_training_data(db) -> tuple:
    """
    Load and prepare all training data from MongoDB.
    Returns (full_df, real_count, synthetic_count, date_range)
    """
    df = load_and_enrich_from_mongo(db)
    total = len(df)
    real_count = (df.get('data_source', pd.Series(['unknown'] * total)) == 'real').sum() if 'data_source' in df.columns else 0
    synth_count = (df.get('data_source', pd.Series(['unknown'] * total)) == 'synthetic').sum() if 'data_source' in df.columns else 0

    logger.info(f"Loaded {total} records: {real_count} real, {synth_count} synthetic")

    if total < 200:
        logger.warning("Very few records in DB. Generating synthetic augmentation for training.")
        from ml.patchtst.dataset import generate_synthetic_augmentation
        synth_df = generate_synthetic_augmentation(days=90)
        synth_df['data_source'] = 'synthetic'
        df = pd.concat([df, synth_df], ignore_index=True).sort_values('timestamp')
        synth_count += len(synth_df)
        total = len(df)
        logger.info(f"After augmentation: {total} records total")

    date_range = {
        "start": str(df['timestamp'].min()) if 'timestamp' in df.columns else "unknown",
        "end": str(df['timestamp'].max()) if 'timestamp' in df.columns else "unknown",
    }
    return df, real_count, synth_count, date_range


def generate_synthetic_augmentation(start_date="2026-01-01", days=90, freq="15min") -> pd.DataFrame:
    """
    Generate controlled synthetic traffic data for training augmentation.
    Based on real distribution observations from Coimbatore corridors.
    Clearly labeled as data_source='synthetic' — NEVER used in test/evaluation sets.
    """
    import math
    dates = pd.date_range(start=start_date, periods=days * 24 * 4, freq=freq, tz="UTC")
    n = len(dates)

    speeds, travel_times, ff_speeds, ff_times = [], [], [], []
    temperatures, precipitations, humidities, wind_speeds = [], [], [], []
    distance_km = 10.0

    for dt in dates:
        hour = dt.hour + dt.minute / 60.0
        weekday = dt.weekday()
        is_weekend = weekday >= 5

        ff_speed = 50.0 + np.random.normal(0, 0.5)
        ff_time = (distance_km / max(ff_speed, 1.0)) * 60.0

        if not is_weekend:
            m_dist = abs(hour - 8.75)
            m_factor = math.exp(-0.5 * (m_dist / 0.85) ** 2) if m_dist < 2.5 else 0.0
            e_dist = abs(hour - 18.25)
            e_factor = math.exp(-0.5 * (e_dist / 1.1) ** 2) if e_dist < 3.0 else 0.0
            mid_dist = abs(hour - 13.5)
            mid_factor = 0.25 * math.exp(-0.5 * (mid_dist / 1.0) ** 2) if mid_dist < 2.0 else 0.0
            congestion_impact = 0.58 * m_factor + 0.65 * e_factor + mid_factor
        else:
            w_mid = abs(hour - 12.5)
            w_mid_factor = 0.40 * math.exp(-0.5 * (w_mid / 1.5) ** 2) if w_mid < 3.0 else 0.0
            w_eve = abs(hour - 19.5)
            w_eve_factor = 0.55 * math.exp(-0.5 * (w_eve / 1.8) ** 2) if w_eve < 3.5 else 0.0
            congestion_impact = w_mid_factor + w_eve_factor

        congestion_impact = min(1.0, max(0.0, congestion_impact))
        temp = 24.0 + 8.0 * math.sin(math.pi * (hour - 8.0) / 12.0) + np.random.normal(0, 0.8)
        rain_prob = 0.12 if (15.0 <= hour <= 20.0 and int(dt.day) % 4 == 0) else 0.01
        rain = np.random.exponential(4.0) if np.random.random() < rain_prob else 0.0
        weather_penalty = 0.22 if rain > 5.0 else 0.12 if rain > 0.5 else 0.0
        humidity = 55.0 + 30.0 * (rain > 0.5) + np.random.normal(0, 5.0)
        wind_spd = 10.0 + np.random.exponential(5.0)

        min_rush_speed = 18.0 if not is_weekend else 22.0
        speed = ff_speed - (ff_speed - min_rush_speed) * congestion_impact
        speed = speed * (1.0 - weather_penalty) + np.random.normal(0, 1.2)
        speed = max(12.0, min(55.0, speed))
        travel_time = (distance_km / speed) * 60.0

        speeds.append(round(speed, 2))
        travel_times.append(round(travel_time, 2))
        ff_speeds.append(round(ff_speed, 2))
        ff_times.append(round(ff_time, 2))
        temperatures.append(round(temp, 1))
        precipitations.append(round(rain, 2))
        humidities.append(round(min(100.0, max(10.0, humidity)), 1))
        wind_speeds.append(round(wind_spd, 1))

    df = pd.DataFrame({
        "timestamp": dates,
        "speed_kmh": speeds,
        "current_travel_time": travel_times,
        "free_flow_speed": ff_speeds,
        "free_flow_travel_time": ff_times,
        "temperature": temperatures,
        "precipitation": precipitations,
        "humidity": humidities,
        "wind_speed": wind_speeds,
        "segment_id": "seg_synthetic_corridor",
        "road_id": "Synthetic-Corridor",
        "data_source": "synthetic",
        "source": "synthetic_augmentation",
    })
    return df


class TrafficDataset(Dataset):
    """
    PyTorch Dataset for PatchTST. Creates sliding window sequences.
    Expects pre-normalized numpy array (data) of shape [T, num_features].
    """
    def __init__(self, data: np.ndarray, config, target_indices: list = None):
        """
        data: np.ndarray of shape [T, num_features], already normalized
        config: PatchTSTConfig
        target_indices: indices in feature dim that are prediction targets
        """
        self.config = config
        self.data = data
        self.target_indices = target_indices or list(range(min(3, data.shape[1])))

        seq_len = config.context_length
        pred_len = config.forecast_horizon
        stride = config.stride

        self.windows = []
        self.targets = []

        for i in range(0, len(data) - seq_len - pred_len + 1, stride):
            x = data[i: i + seq_len]  # [seq_len, num_features]
            y = data[i + seq_len: i + seq_len + pred_len][:, self.target_indices]  # [pred_len, n_targets]
            self.windows.append(x)
            self.targets.append(y)

        self.windows = np.array(self.windows, dtype=np.float32)
        self.targets = np.array(self.targets, dtype=np.float32)

    def __len__(self):
        return len(self.windows)

    def __getitem__(self, idx):
        return torch.tensor(self.windows[idx]), torch.tensor(self.targets[idx])
