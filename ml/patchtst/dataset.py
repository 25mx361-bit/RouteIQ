"""
ml/patchtst/dataset.py — PyTorch Dataset for traffic flow & weather time-series forecasting.
Generates and normalizes realistic diurnal traffic sequences with rush-hour modeling,
weather impacts, and weekend cycles for Coimbatore corridors.
"""
import math
import numpy as np
import torch
from torch.utils.data import Dataset
import pandas as pd
import pickle
from datetime import datetime, timedelta, timezone

FEATURE_COLUMNS = [
    "speed_kmh",
    "current_travel_time",
    "temperature",
    "precipitation",
]

def generate_realistic_traffic_timeseries(start_date="2026-01-01", days=90, freq="15min") -> pd.DataFrame:
    """
    Generate high-fidelity realistic traffic time-series representing urban corridors:
    - Free flow baseline: ~50 km/h (free_flow_travel_time: ~12 min for 10km)
    - Morning Rush (07:45 - 10:15 AM): Peak congestion at 08:45 AM, speed drops to 20-28 km/h.
    - Midday Flow (11:30 AM - 04:00 PM): Moderate flow ~38-44 km/h.
    - Evening Rush (05:00 - 08:30 PM): Peak congestion at 06:15 PM, speed drops to 18-26 km/h.
    - Night Flow (10:30 PM - 05:30 AM): Smooth flow ~48-52 km/h.
    - Weekend Adjustments: Delayed daytime peaks, active evening leisure traffic.
    - Weather impacts: Rain reduces speeds by 15-35%.
    """
    dates = pd.date_range(start=start_date, periods=days * 24 * 4, freq=freq, tz="UTC")
    n = len(dates)
    
    speeds = []
    travel_times = []
    ff_speeds = []
    ff_travel_times = []
    temperatures = []
    precipitations = []
    
    distance_km = 10.0 # Standard 10km reference corridor
    
    for dt in dates:
        hour = dt.hour + dt.minute / 60.0
        weekday = dt.weekday() # 0 = Mon, 6 = Sun
        is_weekend = weekday >= 5
        
        # 1. Base Free-flow speed for corridor
        ff_speed = 50.0 + np.random.normal(0, 0.5)
        ff_time = (distance_km / ff_speed) * 60.0 # ~12.0 mins
        
        # 2. Diurnal congestion profile calculation
        if not is_weekend:
            # Morning Peak (07:30 to 10:30, peak at 08:45 = 8.75)
            m_dist = abs(hour - 8.75)
            m_factor = math.exp(-0.5 * (m_dist / 0.85) ** 2) if m_dist < 2.5 else 0.0
            
            # Evening Peak (16:30 to 20:30, peak at 18.25 = 6:15 PM)
            e_dist = abs(hour - 18.25)
            e_factor = math.exp(-0.5 * (e_dist / 1.1) ** 2) if e_dist < 3.0 else 0.0
            
            # Midday slight dip (13:00 to 14:30)
            mid_dist = abs(hour - 13.5)
            mid_factor = 0.25 * math.exp(-0.5 * (mid_dist / 1.0) ** 2) if mid_dist < 2.0 else 0.0
            
            # Combined congestion impact (0 = free flow, 1 = maximum congestion)
            congestion_impact = 0.58 * m_factor + 0.65 * e_factor + mid_factor
        else:
            # Weekend pattern: late morning peak (11:30 - 13:30) & evening leisure peak (17:30 - 21:30)
            w_mid = abs(hour - 12.5)
            w_mid_factor = 0.40 * math.exp(-0.5 * (w_mid / 1.5) ** 2) if w_mid < 3.0 else 0.0
            
            w_eve = abs(hour - 19.5)
            w_eve_factor = 0.55 * math.exp(-0.5 * (w_eve / 1.8) ** 2) if w_eve < 3.5 else 0.0
            
            congestion_impact = w_mid_factor + w_eve_factor
            
        congestion_impact = min(1.0, max(0.0, congestion_impact))
        
        # 3. Weather simulation (temperature diurnal + occasional rain)
        temp = 24.0 + 8.0 * math.sin(math.pi * (hour - 8.0) / 12.0) + np.random.normal(0, 0.8)
        
        # 8% chance of afternoon/evening showers
        rain_prob = 0.12 if (15.0 <= hour <= 20.0 and dt.day % 4 == 0) else 0.01
        rain = np.random.exponential(4.0) if np.random.random() < rain_prob else 0.0
        
        # Rain speed penalty
        weather_penalty = (0.22 if rain > 5.0 else 0.12 if rain > 0.5 else 0.0)
        
        # 4. Final calculated speed & travel time
        min_rush_speed = 18.0 if not is_weekend else 22.0
        speed = ff_speed - (ff_speed - min_rush_speed) * congestion_impact
        speed = speed * (1.0 - weather_penalty) + np.random.normal(0, 1.2)
        speed = max(12.0, min(55.0, speed))
        
        travel_time = (distance_km / speed) * 60.0
        
        speeds.append(round(speed, 2))
        travel_times.append(round(travel_time, 2))
        ff_speeds.append(round(ff_speed, 2))
        ff_travel_times.append(round(ff_time, 2))
        temperatures.append(round(temp, 1))
        precipitations.append(round(rain, 2))
        
    df = pd.DataFrame({
        "timestamp": dates,
        "speed_kmh": speeds,
        "current_travel_time": travel_times,
        "free_flow_speed": ff_speeds,
        "free_flow_travel_time": ff_travel_times,
        "temperature": temperatures,
        "precipitation": precipitations,
    })
    return df

class TrafficDataset(Dataset):
    def __init__(self, data: pd.DataFrame, config, is_train=True, scaler=None):
        self.config = config
        self.is_train = is_train
        
        # Ensure only numeric feature columns
        df_numeric = data[FEATURE_COLUMNS] if all(c in data.columns for c in FEATURE_COLUMNS) else data.select_dtypes(include=[np.number])
        self.raw_data = df_numeric.values.astype(np.float32)
        
        # Normalization
        if is_train:
            self.mean = np.nanmean(self.raw_data, axis=0)
            self.std = np.nanstd(self.raw_data, axis=0)
            self.std[self.std < 1.0] = 1.0  # Safe minimum std clamp
            self.scaler = (self.mean, self.std)
            with open(self.config.scaler_path, "wb") as f:
                pickle.dump(self.scaler, f)
        else:
            if scaler is None:
                with open(self.config.scaler_path, "rb") as f:
                    self.scaler = pickle.load(f)
            else:
                self.scaler = scaler
            self.mean, self.std = self.scaler
            self.std[self.std < 1.0] = 1.0

        self.data = (self.raw_data - self.mean) / self.std
        
        # Create sliding context windows
        self.windows = []
        self.targets = []
        
        seq_len = self.config.context_length
        pred_len = self.config.forecast_horizon
        stride = self.config.stride
        
        for i in range(0, len(self.data) - seq_len - pred_len + 1, stride):
            x = self.data[i : i + seq_len]
            y = self.data[i + seq_len : i + seq_len + pred_len]
            self.windows.append(x)
            self.targets.append(y)
            
        self.windows = np.array(self.windows)
        self.targets = np.array(self.targets)

    def __len__(self):
        return len(self.windows)

    def __getitem__(self, idx):
        return torch.tensor(self.windows[idx]), torch.tensor(self.targets[idx])

def load_data_from_mongo(db) -> pd.DataFrame:
    """
    Fetch traffic and weather records from MongoDB.
    If database records are sparse (< 500 rows), synthesize a full 90-day high-fidelity
    historical sequence to ensure the neural transformer learns deep diurnal dynamics.
    """
    traffic = []
    if db is not None:
        try:
            traffic = list(db.traffic_data.find().sort("timestamp", 1))
        except Exception:
            traffic = []
            
    if len(traffic) < 500:
        print("[*] Generating realistic 90-day diurnal traffic & weather dataset for PatchTST training...")
        df = generate_realistic_traffic_timeseries(days=90)
        return df[FEATURE_COLUMNS]
        
    df = pd.DataFrame(traffic)
    
    # Map common aliases to standard columns
    if "speed" in df.columns and "speed_kmh" not in df.columns:
        df["speed_kmh"] = df["speed"]
    if "travel_time" in df.columns and "current_travel_time" not in df.columns:
        df["current_travel_time"] = df["travel_time"]
    if "free_flow_speed" not in df.columns:
        df["free_flow_speed"] = 50.0
    if "free_flow_travel_time" not in df.columns:
        df["free_flow_travel_time"] = 12.0
    if "temperature" not in df.columns:
        df["temperature"] = 28.0
    if "precipitation" not in df.columns:
        df["precipitation"] = 0.0

    # Fill NaNs
    df = df.ffill().bfill().fillna(0)
    
    # Return matched feature columns
    available_cols = [c for c in FEATURE_COLUMNS if c in df.columns]
    return df[available_cols]
