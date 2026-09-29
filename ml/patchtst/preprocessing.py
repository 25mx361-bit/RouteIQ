import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import pickle
from pathlib import Path

FEATURE_COLUMNS_ENRICHED = ["speed_kmh", "free_flow_speed", "current_travel_time", "free_flow_travel_time", "temperature", "precipitation", "humidity", "wind_speed", "hour_sin", "hour_cos", "day_of_week", "is_weekend"]

TARGET_COLUMNS = ["speed_kmh", "current_travel_time", "tci"]

def clean_traffic_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values('timestamp')
    df = df[(df['speed_kmh'] > 0) & (df['speed_kmh'].notna())]
    df = df[(df['current_travel_time'] > 0) & (df['current_travel_time'].notna())]
    df = df[(df['free_flow_travel_time'] > 0) & (df['free_flow_travel_time'].notna())]
    df['speed_kmh'] = df['speed_kmh'].clip(lower=1.0, upper=120.0)
    df['current_travel_time'] = df['current_travel_time'].clip(lower=1.0, upper=7200.0)
    df = df.drop_duplicates(subset=['segment_id', 'timestamp'])
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].ffill().bfill()
    df = df.fillna(0)
    return df

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['hour_sin'] = np.sin(2 * np.pi * (df['hour'] + df['minute']/60) / 24)
    df['hour_cos'] = np.cos(2 * np.pi * (df['hour'] + df['minute']/60) / 24)
    df['is_peak_hour'] = ((df['hour'].between(7,10)) | (df['hour'].between(16,20))).astype(int)
    return df

def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    df['tci'] = df['current_travel_time'] / df['free_flow_travel_time'].clip(lower=1.0)
    df['tci'] = df['tci'].clip(lower=0.5, upper=10.0)
    return df

def fill_missing_weather(df: pd.DataFrame) -> pd.DataFrame:
    if 'temperature' not in df.columns:
        df['temperature'] = 28.0
    elif df['temperature'].isna().mean() > 0.9:
        df['temperature'] = df['temperature'].fillna(28.0)

    if 'precipitation' not in df.columns:
        df['precipitation'] = 0.0
    if 'humidity' not in df.columns:
        df['humidity'] = 65.0
    if 'wind_speed' not in df.columns:
        df['wind_speed'] = 10.0
        
    weather_cols = ['temperature', 'precipitation', 'humidity', 'wind_speed']
    for col in weather_cols:
        if col in df.columns:
            df[col] = df[col].ffill()
    
    df['temperature'] = df['temperature'].fillna(28.0)
    df['precipitation'] = df['precipitation'].fillna(0.0)
    df['humidity'] = df['humidity'].fillna(65.0)
    df['wind_speed'] = df['wind_speed'].fillna(10.0)
    
    return df

def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_traffic_df(df)
    df = add_time_features(df)
    df = add_derived_features(df)
    df = fill_missing_weather(df)
    
    available_cols = [c for c in FEATURE_COLUMNS_ENRICHED if c in df.columns]
    feature_df = df[available_cols].copy()
    
    for col in FEATURE_COLUMNS_ENRICHED:
        if col not in feature_df.columns:
            feature_df[col] = 0.0
            
    return feature_df[FEATURE_COLUMNS_ENRICHED]

def chronological_split(df: pd.DataFrame, train_pct=0.70, val_pct=0.15) -> tuple:
    if 'timestamp' in df.columns:
        df = df.sort_values('timestamp')
    else:
        df = df.sort_index()
    n = len(df)
    train_end = int(n * train_pct)
    val_end = int(n * (train_pct + val_pct))
    return (df.iloc[:train_end], df.iloc[train_end:val_end], df.iloc[val_end:])

def fit_scaler(df: pd.DataFrame, scaler_path: Path) -> tuple:
    scaler = StandardScaler()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    scaler.fit(df[numeric_cols])
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    mean_array = scaler.mean_
    std_array = np.sqrt(scaler.var_)
    return (mean_array, std_array)

def apply_scaler(df: pd.DataFrame, scaler_path: Path) -> np.ndarray:
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    return scaler.transform(df[numeric_cols])
